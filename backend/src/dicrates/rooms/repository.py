import uuid
from typing import Any, Protocol

import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from dicrates.rooms.models import ACTIVE_STATUSES, JoinOutcome, NewRoom, Room, StartOutcome


class InviteCodeTakenError(Exception):
    """Another active room uses the code; the caller retries with a new one."""


class RoomRepository(Protocol):
    async def create(self, new_room: NewRoom, *, creator_id: uuid.UUID) -> Room: ...

    async def get(self, room_id: uuid.UUID) -> Room | None: ...

    async def find_active_by_code(self, code: str) -> Room | None: ...

    async def is_member(self, room_id: uuid.UUID, user_id: uuid.UUID) -> bool: ...

    async def list_for_member(self, user_id: uuid.UUID) -> list[Room]: ...

    async def add_member(
        self, room_id: uuid.UUID, user_id: uuid.UUID, *, max_members: int
    ) -> JoinOutcome: ...

    async def start(
        self, room_id: uuid.UUID, *, min_members: int, max_members: int
    ) -> StartOutcome: ...

    async def remove_member(self, room_id: uuid.UUID, user_id: uuid.UUID) -> bool: ...

    async def dissolve(self, room_id: uuid.UUID) -> bool: ...


_SELECT = sql.SQL(
    "SELECT r.id, r.question_id, r.language, r.round_duration_hours, r.invite_code, r.status,"
    " r.creator_id, r.created_at, r.started_at,"
    " (SELECT count(*) FROM public.room_members m"
    "  WHERE m.room_id = r.id AND m.left_at IS NULL) AS member_count"
    " FROM public.rooms r"
)
_ACTIVE = [status.value for status in ACTIVE_STATUSES]


class PostgresRoomRepository:
    """Membership changes lock the room row (`FOR UPDATE`) so limits hold under concurrency."""

    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._pool = pool

    async def _rooms(self, where: str, params: dict[str, Any]) -> list[Room]:
        async with self._pool.connection() as connection:
            cursor = connection.cursor(row_factory=dict_row)
            await cursor.execute(_SELECT + sql.SQL(" " + where), params)  # pyright: ignore[reportArgumentType]
            return [Room.model_validate(row) for row in await cursor.fetchall()]

    async def create(self, new_room: NewRoom, *, creator_id: uuid.UUID) -> Room:
        room_id = uuid.uuid4()
        try:
            async with self._pool.connection() as connection, connection.transaction():
                await connection.execute(
                    "INSERT INTO public.rooms (id, question_id, language, round_duration_hours,"
                    " invite_code, creator_id) VALUES (%s, %s, %s, %s, %s, %s)",
                    (
                        room_id,
                        new_room.question_id,
                        new_room.language,
                        new_room.round_duration_hours,
                        new_room.invite_code,
                        creator_id,
                    ),
                )
                await connection.execute(
                    "INSERT INTO public.room_members (room_id, user_id) VALUES (%s, %s)",
                    (room_id, creator_id),
                )
        except psycopg.errors.UniqueViolation as error:
            raise InviteCodeTakenError from error
        room = await self.get(room_id)
        assert room is not None  # noqa: S101 - just inserted
        return room

    async def get(self, room_id: uuid.UUID) -> Room | None:
        found = await self._rooms("WHERE r.id = %(id)s", {"id": room_id})
        return found[0] if found else None

    async def find_active_by_code(self, code: str) -> Room | None:
        found = await self._rooms(
            "WHERE r.invite_code = %(code)s AND r.status = ANY(%(active)s)",
            {"code": code, "active": _ACTIVE},
        )
        return found[0] if found else None

    async def is_member(self, room_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        async with self._pool.connection() as connection:
            cursor = await connection.execute(
                "SELECT 1 FROM public.room_members"
                " WHERE room_id = %s AND user_id = %s AND left_at IS NULL",
                (room_id, user_id),
            )
            return await cursor.fetchone() is not None

    async def list_for_member(self, user_id: uuid.UUID) -> list[Room]:
        return await self._rooms(
            "WHERE EXISTS (SELECT 1 FROM public.room_members m WHERE m.room_id = r.id"
            " AND m.user_id = %(user)s AND m.left_at IS NULL) ORDER BY r.created_at DESC",
            {"user": user_id},
        )

    async def add_member(
        self, room_id: uuid.UUID, user_id: uuid.UUID, *, max_members: int
    ) -> JoinOutcome:
        async with self._pool.connection() as connection, connection.transaction():
            cursor = await connection.execute(
                "SELECT status FROM public.rooms WHERE id = %s FOR UPDATE", (room_id,)
            )
            row = await cursor.fetchone()
            if row is None:
                return JoinOutcome.NOT_FORMING
            member = await connection.execute(
                "SELECT left_at IS NULL FROM public.room_members"
                " WHERE room_id = %s AND user_id = %s",
                (room_id, user_id),
            )
            existing = await member.fetchone()
            if existing is not None and existing[0]:
                return JoinOutcome.ALREADY_MEMBER
            if row[0] != "FORMING":
                return JoinOutcome.NOT_FORMING
            count = await connection.execute(
                "SELECT count(*) FROM public.room_members WHERE room_id = %s AND left_at IS NULL",
                (room_id,),
            )
            active = await count.fetchone()
            if active is not None and active[0] >= max_members:
                return JoinOutcome.FULL
            await connection.execute(
                "INSERT INTO public.room_members (room_id, user_id) VALUES (%s, %s)"
                " ON CONFLICT (room_id, user_id) DO UPDATE SET left_at = NULL, joined_at = now()",
                (room_id, user_id),
            )
            return JoinOutcome.ADDED

    async def start(
        self, room_id: uuid.UUID, *, min_members: int, max_members: int
    ) -> StartOutcome:
        async with self._pool.connection() as connection, connection.transaction():
            cursor = await connection.execute(
                "SELECT status FROM public.rooms WHERE id = %s FOR UPDATE", (room_id,)
            )
            row = await cursor.fetchone()
            if row is None or row[0] != "FORMING":
                return StartOutcome.NOT_FORMING
            count = await connection.execute(
                "SELECT count(*) FROM public.room_members WHERE room_id = %s AND left_at IS NULL",
                (room_id,),
            )
            active = await count.fetchone()
            if active is None or not min_members <= active[0] <= max_members:
                return StartOutcome.TOO_FEW
            # Task 10 hooks the round deadlines and jobs into this transaction.
            await connection.execute(
                "UPDATE public.rooms SET status = 'R1_OPEN', started_at = now() WHERE id = %s",
                (room_id,),
            )
            return StartOutcome.STARTED

    async def remove_member(self, room_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        async with self._pool.connection() as connection, connection.transaction():
            cursor = await connection.execute(
                "UPDATE public.room_members m SET left_at = now() FROM public.rooms r"
                " WHERE m.room_id = r.id AND r.id = %s AND m.user_id = %s"
                " AND m.left_at IS NULL AND r.status = 'FORMING'",
                (room_id, user_id),
            )
            return cursor.rowcount == 1

    async def dissolve(self, room_id: uuid.UUID) -> bool:
        async with self._pool.connection() as connection:
            cursor = await connection.execute(
                "UPDATE public.rooms SET status = 'ABORTED' WHERE id = %s AND status = 'FORMING'",
                (room_id,),
            )
            return cursor.rowcount == 1
