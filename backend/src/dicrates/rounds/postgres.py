"""Postgres unit of work for the round engine (one transaction, room row locked)."""

import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

import psycopg
from procrastinate import exceptions as procrastinate_exceptions
from psycopg_pool import AsyncConnectionPool

from dicrates.jobs.app import app as jobs_app
from dicrates.rooms.models import RoomStatus
from dicrates.rounds.engine import LockedRoom, ScheduledJob, UnitOfWorkFactory


class PostgresUnitOfWork:
    def __init__(self, connection: psycopg.AsyncConnection[tuple[object, ...]]) -> None:
        self._connection = connection

    async def lock_room(self, room_id: uuid.UUID) -> LockedRoom | None:
        cursor = await self._connection.execute(
            "SELECT r.id, r.status, r.round_duration_hours, r.created_at,"
            " (SELECT count(*) FROM public.room_members m"
            "  WHERE m.room_id = r.id AND m.left_at IS NULL)"
            " FROM public.rooms r WHERE r.id = %s FOR UPDATE OF r",
            (room_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        room, status, hours, created_at, members = row
        return LockedRoom(
            id=room,  # pyright: ignore[reportArgumentType]
            status=RoomStatus(status),
            round_duration_hours=hours,  # pyright: ignore[reportArgumentType]
            created_at=created_at,  # pyright: ignore[reportArgumentType]
            member_count=members,  # pyright: ignore[reportArgumentType]
        )

    async def set_status(self, room_id: uuid.UUID, status: RoomStatus, *, now: datetime) -> None:
        await self._connection.execute(
            "UPDATE public.rooms SET status = %s,"
            " started_at = CASE WHEN %s = 'R1_OPEN' THEN %s ELSE started_at END,"
            " finished_at = CASE WHEN %s = 'FINISHED' THEN %s ELSE finished_at END"
            " WHERE id = %s",
            (status.value, status.value, now, status.value, now, room_id),
        )

    async def open_round(
        self, room_id: uuid.UUID, number: int, *, opened_at: datetime, deadline_at: datetime
    ) -> None:
        await self._connection.execute(
            "INSERT INTO public.rounds (room_id, number, opened_at, deadline_at)"
            " VALUES (%s, %s, %s, %s) ON CONFLICT (room_id, number) DO NOTHING",
            (room_id, number, opened_at, deadline_at),
        )

    async def close_round(self, room_id: uuid.UUID, number: int, *, closed_at: datetime) -> None:
        await self._connection.execute(
            "UPDATE public.rounds SET closed_at = %s"
            " WHERE room_id = %s AND number = %s AND closed_at IS NULL",
            (closed_at, room_id, number),
        )

    async def submission_count(self, room_id: uuid.UUID, number: int) -> int:
        cursor = await self._connection.execute(
            "SELECT count(*) FROM public.round_participation p"
            " JOIN public.room_members m ON m.room_id = p.room_id AND m.user_id = p.user_id"
            " WHERE p.room_id = %s AND p.round_number = %s AND m.left_at IS NULL",
            (room_id, number),
        )
        row = await cursor.fetchone()
        return int(row[0]) if row else 0  # pyright: ignore[reportArgumentType]

    async def schedule(self, job: ScheduledJob) -> None:
        try:
            # Savepoint: a queueing-lock conflict must not abort the outer transaction.
            async with self._connection.transaction():
                await jobs_app.configure_task(
                    job.task,
                    schedule_at=job.at,
                    queueing_lock=job.queueing_lock,
                    connection=self._connection,
                ).defer_async(**job.args)
        except procrastinate_exceptions.AlreadyEnqueued:
            pass

    async def forming_rooms_created_before(self, cutoff: datetime) -> list[uuid.UUID]:
        cursor = await self._connection.execute(
            "SELECT id FROM public.rooms WHERE status = 'FORMING' AND created_at < %s",
            (cutoff,),
        )
        return [row[0] for row in await cursor.fetchall()]  # pyright: ignore[reportReturnType]


def postgres_unit_of_work(pool: AsyncConnectionPool) -> UnitOfWorkFactory:
    @asynccontextmanager
    async def unit_of_work() -> AsyncGenerator[PostgresUnitOfWork]:
        async with pool.connection() as connection, connection.transaction():
            yield PostgresUnitOfWork(connection)

    return unit_of_work
