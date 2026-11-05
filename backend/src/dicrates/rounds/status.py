"""Read model for `GET /rooms/{id}/status`: phase, deadline and counts (no opinions)."""

import uuid
from datetime import datetime
from typing import Protocol

from psycopg.rows import class_row
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel


class RoundStatusView(BaseModel):
    status: str
    #: The current or last round with submissions (1-3), `None` before the start.
    round_number: int | None
    deadline_at: datetime | None
    #: Whether the caller has submitted in that round.
    submitted: bool
    #: How many members submitted ("3 of 5"); reveals no distribution of opinions.
    submission_count: int
    member_count: int


class RoundStatusReader(Protocol):
    async def status(self, room_id: uuid.UUID, user_id: uuid.UUID) -> RoundStatusView: ...


class PostgresRoundStatusReader:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._pool = pool

    async def status(self, room_id: uuid.UUID, user_id: uuid.UUID) -> RoundStatusView:
        async with self._pool.connection() as connection:
            cursor = connection.cursor(row_factory=class_row(RoundStatusView))
            await cursor.execute(
                "SELECT r.status, rd.number AS round_number,"
                " CASE WHEN rd.closed_at IS NULL THEN rd.deadline_at END AS deadline_at,"
                " EXISTS (SELECT 1 FROM public.round_participation p WHERE p.room_id = r.id"
                "  AND p.round_number = rd.number AND p.user_id = %(user)s) AS submitted,"
                " (SELECT count(*) FROM public.round_participation p"
                "  JOIN public.room_members m ON m.room_id = p.room_id AND m.user_id = p.user_id"
                "  WHERE p.room_id = r.id AND p.round_number = rd.number"
                "  AND m.left_at IS NULL) AS submission_count,"
                " (SELECT count(*) FROM public.room_members m"
                "  WHERE m.room_id = r.id AND m.left_at IS NULL) AS member_count"
                " FROM public.rooms r"
                " LEFT JOIN LATERAL (SELECT * FROM public.rounds x WHERE x.room_id = r.id"
                "  ORDER BY x.number DESC LIMIT 1) rd ON true"
                " WHERE r.id = %(room)s",
                {"room": room_id, "user": user_id},
            )
            view = await cursor.fetchone()
        if view is None:
            msg = f"room {room_id} not found"
            raise LookupError(msg)
        return view
