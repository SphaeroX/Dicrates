"""In-memory unit of work for engine unit tests."""

import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime

from dicrates.rooms.models import RoomStatus
from dicrates.rounds.engine import LockedRoom, ScheduledJob


@dataclass
class FakeRoom:
    status: RoomStatus
    round_duration_hours: int = 1
    created_at: datetime = datetime(2026, 11, 1, 12, 0)
    members: set[uuid.UUID] = field(default_factory=set[uuid.UUID])
    finished_at: datetime | None = None


@dataclass
class FakeRound:
    opened_at: datetime
    deadline_at: datetime
    closed_at: datetime | None = None
    submitted: set[uuid.UUID] = field(default_factory=set[uuid.UUID])


class FakeWorld:
    def __init__(self) -> None:
        self.rooms: dict[uuid.UUID, FakeRoom] = {}
        self.rounds: dict[tuple[uuid.UUID, int], FakeRound] = {}
        self.jobs: list[ScheduledJob] = []
        self.transactions = 0

    def add_room(self, status: RoomStatus, *, members: int = 3, **kwargs: object) -> uuid.UUID:
        room_id = uuid.uuid4()
        self.rooms[room_id] = FakeRoom(
            status=status,
            members={uuid.uuid4() for _ in range(members)},
            **kwargs,  # type: ignore[arg-type]
        )
        return room_id

    def submit(self, room_id: uuid.UUID, number: int, count: int) -> None:
        members = sorted(self.rooms[room_id].members)
        self.rounds[(room_id, number)].submitted.update(members[:count])

    def jobs_named(self, task: str) -> list[ScheduledJob]:
        return [job for job in self.jobs if job.task == task]

    @asynccontextmanager
    async def unit_of_work(self) -> AsyncGenerator[FakeUnitOfWork]:
        self.transactions += 1
        yield FakeUnitOfWork(self)


class FakeUnitOfWork:
    def __init__(self, world: FakeWorld) -> None:
        self.world = world

    async def lock_room(self, room_id: uuid.UUID) -> LockedRoom | None:
        room = self.world.rooms.get(room_id)
        if room is None:
            return None
        return LockedRoom(
            id=room_id,
            status=room.status,
            round_duration_hours=room.round_duration_hours,
            created_at=room.created_at,
            member_count=len(room.members),
        )

    async def set_status(self, room_id: uuid.UUID, status: RoomStatus, *, now: datetime) -> None:
        room = self.world.rooms[room_id]
        room.status = status
        if status is RoomStatus.FINISHED:
            room.finished_at = now

    async def open_round(
        self, room_id: uuid.UUID, number: int, *, opened_at: datetime, deadline_at: datetime
    ) -> None:
        self.world.rounds[(room_id, number)] = FakeRound(opened_at, deadline_at)

    async def close_round(self, room_id: uuid.UUID, number: int, *, closed_at: datetime) -> None:
        self.world.rounds[(room_id, number)].closed_at = closed_at

    async def submission_count(self, room_id: uuid.UUID, number: int) -> int:
        round_ = self.world.rounds.get((room_id, number))
        if round_ is None:
            return 0
        return len(round_.submitted & self.world.rooms[room_id].members)

    async def schedule(self, job: ScheduledJob) -> None:
        if job.queueing_lock and any(
            existing.queueing_lock == job.queueing_lock for existing in self.world.jobs
        ):
            return
        self.world.jobs.append(job)

    async def forming_rooms_created_before(self, cutoff: datetime) -> list[uuid.UUID]:
        return [
            room_id
            for room_id, room in self.world.rooms.items()
            if room.status is RoomStatus.FORMING and room.created_at < cutoff
        ]
