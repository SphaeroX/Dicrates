import uuid
from datetime import datetime, timedelta

import pytest
from tests.rounds.fakes import FakeWorld

from dicrates.rooms.models import RoomStatus as S
from dicrates.rounds.engine import (
    MIN_ROUND1_SUBMISSIONS,
    FixedClock,
    HookRegistry,
    RoundEngine,
    StartRejectedError,
)
from dicrates.rounds.state_machine import Event

NOW = datetime(2026, 11, 5, 12, 0)


@pytest.fixture
def world() -> FakeWorld:
    return FakeWorld()


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(NOW)


def engine(world: FakeWorld, clock: FixedClock, hooks: HookRegistry | None = None) -> RoundEngine:
    return RoundEngine(world.unit_of_work, clock=clock, hooks=hooks or HookRegistry())


async def test_start_opens_round_one_and_schedules_its_close(
    world: FakeWorld, clock: FixedClock
) -> None:
    room = world.add_room(S.FORMING, members=3, round_duration_hours=6)

    status = await engine(world, clock).start(room)

    assert status is S.R1_OPEN
    round_one = world.rounds[(room, 1)]
    assert round_one.opened_at == NOW
    assert round_one.deadline_at == NOW + timedelta(hours=6)
    [job] = world.jobs
    assert (job.task, job.args, job.at) == (
        "close_round",
        {"room_id": str(room), "round_number": 1},
        NOW + timedelta(hours=6),
    )


@pytest.mark.parametrize("members", [2, 7])
async def test_start_needs_three_to_six_members(
    world: FakeWorld, clock: FixedClock, members: int
) -> None:
    room = world.add_room(S.FORMING, members=members)

    with pytest.raises(StartRejectedError):
        await engine(world, clock).start(room)

    assert world.rooms[room].status is S.FORMING
    assert world.jobs == []


async def test_close_job_twice_has_the_same_result(world: FakeWorld, clock: FixedClock) -> None:
    room = world.add_room(S.FORMING)
    rounds = engine(world, clock)
    await rounds.start(room)
    world.submit(room, 1, 3)

    first = await rounds.close_round(room, 1)
    second = await rounds.close_round(room, 1)

    assert first is S.R1_CLOSED
    assert second is S.R1_CLOSED
    assert len(world.jobs_named("after_status")) == 1


async def test_round_one_with_too_few_submissions_aborts(
    world: FakeWorld, clock: FixedClock
) -> None:
    room = world.add_room(S.FORMING, members=4)
    rounds = engine(world, clock)
    await rounds.start(room)
    world.submit(room, 1, MIN_ROUND1_SUBMISSIONS - 1)

    status = await rounds.close_round(room, 1)

    assert status is S.ABORTED
    assert world.jobs_named("after_status") == []


async def test_later_rounds_continue_with_few_submissions(
    world: FakeWorld, clock: FixedClock
) -> None:
    room = world.add_room(S.R2_CLOSED)
    rounds = engine(world, clock)
    await rounds.after_status(room, S.R2_CLOSED)  # opens round 3

    status = await rounds.close_round(room, 3)  # nobody submitted

    assert status is S.R3_CLOSED


async def test_early_close_when_everyone_submitted(world: FakeWorld, clock: FixedClock) -> None:
    room = world.add_room(S.FORMING, members=3)
    rounds = engine(world, clock)
    await rounds.start(room)

    world.submit(room, 1, 2)
    assert await rounds.close_if_complete(room, 1) is S.R1_OPEN
    world.submit(room, 1, 3)
    assert await rounds.close_if_complete(room, 1) is S.R1_CLOSED
    assert world.rounds[(room, 1)].closed_at == NOW


async def test_stale_jobs_are_ignored(world: FakeWorld, clock: FixedClock) -> None:
    room = world.add_room(S.R2_OPEN)

    assert await engine(world, clock).close_round(room, 1) is S.R2_OPEN
    assert await engine(world, clock).after_status(room, S.R1_CLOSED) is S.R2_OPEN
    assert world.jobs == []


async def test_hooks_run_before_advancing(world: FakeWorld, clock: FixedClock) -> None:
    calls: list[tuple[S, uuid.UUID]] = []
    hooks = HookRegistry()

    async def group_picture(room_id: uuid.UUID) -> None:
        calls.append((S.R1_CLOSED, room_id))

    hooks.register(S.R1_CLOSED, group_picture)
    room = world.add_room(S.R1_CLOSED)

    status = await engine(world, clock, hooks).after_status(room, S.R1_CLOSED)

    assert calls == [(S.R1_CLOSED, room)]
    assert status is S.R2_OPEN
    assert world.jobs_named("close_round")[0].args["round_number"] == 2


async def test_failing_hook_keeps_the_status(world: FakeWorld, clock: FixedClock) -> None:
    hooks = HookRegistry()

    async def broken(room_id: uuid.UUID) -> None:
        raise RuntimeError("llm down")

    hooks.register(S.R1_CLOSED, broken)
    room = world.add_room(S.R1_CLOSED)

    with pytest.raises(RuntimeError):
        await engine(world, clock, hooks).after_status(room, S.R1_CLOSED)

    assert world.rooms[room].status is S.R1_CLOSED


async def test_full_run_to_finished_with_noop_hooks(world: FakeWorld, clock: FixedClock) -> None:
    room = world.add_room(S.FORMING, members=3)
    rounds = engine(world, clock)

    await rounds.start(room)
    world.submit(room, 1, 3)
    for number, closed in ((1, S.R1_CLOSED), (2, S.R2_CLOSED), (3, S.R3_CLOSED)):
        clock.now_value += timedelta(hours=1)
        await rounds.close_round(room, number)
        await rounds.after_status(room, closed)
    status = await rounds.after_status(room, S.R4_EVALUATING)

    assert status is S.FINISHED
    [archive] = world.jobs_named("archive_room")
    assert archive.at == clock.now_value + timedelta(days=30)
    assert await rounds.archive(room) is S.ARCHIVED


async def test_forming_rooms_expire_after_seven_days(world: FakeWorld, clock: FixedClock) -> None:
    old = world.add_room(S.FORMING, created_at=NOW - timedelta(days=8))
    fresh = world.add_room(S.FORMING, created_at=NOW - timedelta(days=2))
    running = world.add_room(S.R1_OPEN, created_at=NOW - timedelta(days=9))

    expired = await engine(world, clock).expire_forming_rooms()

    assert expired == 1
    assert world.rooms[old].status is S.ABORTED
    assert world.rooms[fresh].status is S.FORMING
    assert world.rooms[running].status is S.R1_OPEN


async def test_unknown_room_is_a_noop(world: FakeWorld, clock: FixedClock) -> None:
    assert await engine(world, clock).close_round(uuid.uuid4(), 1) is None


def test_events_are_exhaustive() -> None:
    assert {event.value for event in Event} >= {"start", "close", "advance", "finish"}
