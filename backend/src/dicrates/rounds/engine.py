"""Applies round transitions: lock the room, change status, open/close rounds, queue jobs.

Every change happens in one unit of work (one DB transaction with the room row
locked), and follow-up jobs are queued in that same transaction. Each public
method takes the status it expects; if the room has moved on, the call is a no-op,
so repeated or concurrent jobs end in the same state without duplicate jobs.

Automatic transitions run only in jobs (`dicrates.rounds.jobs`). The one
user-triggered transition is the creator's start, which uses `start()` from the
API request with the same locking.
"""

import logging
import uuid
from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

from dicrates.rooms.models import MAX_MEMBERS, MIN_MEMBERS, RoomStatus
from dicrates.rounds.state_machine import (
    Event,
    closed_round_number,
    next_status,
    open_round_number,
)

logger = logging.getLogger(__name__)

#: Round 1 needs this many valid submissions, otherwise the game is aborted.
MIN_ROUND1_SUBMISSIONS = 3
FORMING_LIFETIME = timedelta(days=7)
DEFAULT_ARCHIVE_AFTER = timedelta(days=30)

S = RoomStatus


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


@dataclass
class FixedClock:
    now_value: datetime

    def now(self) -> datetime:
        return self.now_value


@dataclass(frozen=True)
class LockedRoom:
    id: uuid.UUID
    status: RoomStatus
    round_duration_hours: int
    created_at: datetime
    member_count: int


@dataclass(frozen=True)
class ScheduledJob:
    task: str
    args: dict[str, Any]
    at: datetime
    queueing_lock: str | None = None


class UnitOfWork(Protocol):
    """One transaction; `lock_room` locks the room row until the end."""

    async def lock_room(self, room_id: uuid.UUID) -> LockedRoom | None: ...

    async def set_status(
        self, room_id: uuid.UUID, status: RoomStatus, *, now: datetime
    ) -> None: ...

    async def open_round(
        self, room_id: uuid.UUID, number: int, *, opened_at: datetime, deadline_at: datetime
    ) -> None: ...

    async def close_round(
        self, room_id: uuid.UUID, number: int, *, closed_at: datetime
    ) -> None: ...

    async def submission_count(self, room_id: uuid.UUID, number: int) -> int: ...

    async def schedule(self, job: ScheduledJob) -> None: ...

    async def forming_rooms_created_before(self, cutoff: datetime) -> list[uuid.UUID]: ...


type UnitOfWorkFactory = Callable[[], AbstractAsyncContextManager[UnitOfWork]]
type Hook = Callable[[uuid.UUID], Awaitable[None]]


@dataclass
class HookRegistry:
    """Steps that must run after a status before the room moves on.

    E.g. `register(R1_CLOSED, write_group_picture)` (Task 13). Without hooks a
    closed status advances right away. Hooks run outside the room lock and must
    be idempotent; if one fails the job is retried and the status stays.
    """

    _hooks: dict[RoomStatus, list[Hook]] = field(default_factory=dict[RoomStatus, list[Hook]])

    def register(self, status: RoomStatus, hook: Hook) -> None:
        self._hooks.setdefault(status, []).append(hook)

    async def run(self, status: RoomStatus, room_id: uuid.UUID) -> None:
        for hook in self._hooks.get(status, []):
            await hook(room_id)


class StartRejectedError(Exception):
    """The room cannot start: not forming or not 3-6 members."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


_AFTER_EVENTS = {
    S.R1_CLOSED: Event.ADVANCE,
    S.R2_CLOSED: Event.ADVANCE,
    S.R3_CLOSED: Event.ADVANCE,
    S.R4_EVALUATING: Event.FINISH,
}


class RoundEngine:
    def __init__(
        self,
        unit_of_work: UnitOfWorkFactory,
        *,
        clock: Clock | None = None,
        hooks: HookRegistry | None = None,
        archive_after: timedelta = DEFAULT_ARCHIVE_AFTER,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._clock = clock or SystemClock()
        self._hooks = hooks or HookRegistry()
        self._archive_after = archive_after

    async def _apply(
        self, uow: UnitOfWork, room: LockedRoom, event: Event, now: datetime
    ) -> RoomStatus:
        if event is Event.CLOSE and room.status is S.R1_OPEN:
            submissions = await uow.submission_count(room.id, 1)
            if submissions < MIN_ROUND1_SUBMISSIONS:
                event = Event.ABORT
        new = next_status(room.status, event)
        await uow.set_status(room.id, new, now=now)

        open_number = open_round_number(room.status)
        if open_number is not None:  # leaving an open round (close or abort)
            await uow.close_round(room.id, open_number, closed_at=now)

        new_open = open_round_number(new)
        if new_open is not None:
            deadline = now + timedelta(hours=room.round_duration_hours)
            await uow.open_round(room.id, new_open, opened_at=now, deadline_at=deadline)
            await uow.schedule(
                ScheduledJob(
                    task="close_round",
                    args={"room_id": str(room.id), "round_number": new_open},
                    at=deadline,
                    queueing_lock=f"close_round:{room.id}:{new_open}",
                )
            )
        elif new in _AFTER_EVENTS:
            await uow.schedule(
                ScheduledJob(
                    task="after_status",
                    args={"room_id": str(room.id), "status": new.value},
                    at=now,
                    queueing_lock=f"after_status:{room.id}:{new.value}",
                )
            )
        elif new is S.FINISHED:
            await uow.schedule(
                ScheduledJob(
                    task="archive_room",
                    args={"room_id": str(room.id)},
                    at=now + self._archive_after,
                    queueing_lock=f"archive_room:{room.id}",
                )
            )
        logger.info("room %s: %s -%s-> %s", room.id, room.status, event, new)
        return new

    async def _transition(
        self, room_id: uuid.UUID, event: Event, *, expected: RoomStatus
    ) -> RoomStatus | None:
        async with self._unit_of_work() as uow:
            room = await uow.lock_room(room_id)
            if room is None:
                return None
            if room.status is not expected:
                return room.status  # stale or repeated job: nothing to do
            return await self._apply(uow, room, event, self._clock.now())

    async def start(self, room_id: uuid.UUID) -> RoomStatus:
        async with self._unit_of_work() as uow:
            room = await uow.lock_room(room_id)
            if room is None or room.status is not S.FORMING:
                raise StartRejectedError("not_forming")
            if not MIN_MEMBERS <= room.member_count <= MAX_MEMBERS:
                raise StartRejectedError("too_few")
            return await self._apply(uow, room, Event.START, self._clock.now())

    async def close_round(self, room_id: uuid.UUID, round_number: int) -> RoomStatus | None:
        """Deadline job: close round `round_number` if it is still open."""
        expected = {1: S.R1_OPEN, 2: S.R2_OPEN, 3: S.R3_OPEN}[round_number]
        return await self._transition(room_id, Event.CLOSE, expected=expected)

    async def close_if_complete(self, room_id: uuid.UUID, round_number: int) -> RoomStatus | None:
        """Called after each submission (Task 11): close early once all members submitted."""
        expected = {1: S.R1_OPEN, 2: S.R2_OPEN, 3: S.R3_OPEN}[round_number]
        async with self._unit_of_work() as uow:
            room = await uow.lock_room(room_id)
            if room is None or room.status is not expected:
                return None if room is None else room.status
            if await uow.submission_count(room_id, round_number) < room.member_count:
                return room.status
            return await self._apply(uow, room, Event.CLOSE, self._clock.now())

    async def after_status(self, room_id: uuid.UUID, status: RoomStatus) -> RoomStatus | None:
        """Run the hooks registered for `status`, then move on (idempotent)."""
        async with self._unit_of_work() as uow:
            room = await uow.lock_room(room_id)
        if room is None or room.status is not status or status not in _AFTER_EVENTS:
            return None if room is None else room.status
        await self._hooks.run(status, room_id)
        return await self._transition(room_id, _AFTER_EVENTS[status], expected=status)

    async def archive(self, room_id: uuid.UUID) -> RoomStatus | None:
        return await self._transition(room_id, Event.ARCHIVE, expected=S.FINISHED)

    async def expire_forming_rooms(self) -> int:
        cutoff = self._clock.now() - FORMING_LIFETIME
        async with self._unit_of_work() as uow:
            candidates = await uow.forming_rooms_created_before(cutoff)
        expired = 0
        for room_id in candidates:
            if await self._transition(room_id, Event.EXPIRE, expected=S.FORMING) is S.ABORTED:
                expired += 1
        return expired


def round_number_closed_by(status: RoomStatus) -> int | None:
    return closed_round_number(status)
