"""Round engine on Postgres with the real Procrastinate worker (local Supabase stack)."""

import asyncio
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import pytest
from procrastinate import PsycopgConnector
from psycopg_pool import AsyncConnectionPool
from tests.questions.factories import make_content

from dicrates.core.db import create_pool
from dicrates.core.language import Language
from dicrates.jobs.app import app as jobs_app
from dicrates.jobs.resources import resources
from dicrates.questions.repository import PostgresQuestionRepository
from dicrates.rooms.models import NewRoom, RoomStatus
from dicrates.rooms.repository import PostgresRoomRepository
from dicrates.rounds.engine import FixedClock, HookRegistry, RoundEngine
from dicrates.rounds.postgres import postgres_unit_of_work
from dicrates.rounds.status import PostgresRoundStatusReader

pytestmark = pytest.mark.integration

#: Far enough in the past that every deadline computed from it is already due.
PAST = datetime.now(UTC) - timedelta(days=3)


class World:
    def __init__(self, pool: AsyncConnectionPool, database_url: str) -> None:
        self.pool = pool
        self.database_url = database_url
        self.users: list[uuid.UUID] = []
        self.questions: list[uuid.UUID] = []
        self.clock = FixedClock(PAST)

    async def user(self) -> uuid.UUID:
        user_id = uuid.uuid4()
        async with self.pool.connection() as connection:
            await connection.execute(
                "INSERT INTO auth.users (id, email) VALUES (%s, %s)",
                (user_id, f"{user_id}@example.test"),
            )
        self.users.append(user_id)
        return user_id

    async def room(self, members: int) -> tuple[uuid.UUID, list[uuid.UUID]]:
        question = await PostgresQuestionRepository(self.pool).create(make_content())
        self.questions.append(question.id)
        rooms = PostgresRoomRepository(self.pool, clock=self.clock)
        creator = await self.user()
        code = "".join("ABCDEFGHJKMNPQRTUVWXYZ2346789"[b % 29] for b in uuid.uuid4().bytes[:6])
        room = await rooms.create(
            NewRoom(
                question_id=question.id,
                language=Language.EN,
                round_duration_hours=1,
                invite_code=code,
            ),
            creator_id=creator,
        )
        others = [await self.user() for _ in range(members - 1)]
        for other in others:
            await rooms.add_member(room.id, other, max_members=6)
        return room.id, [creator, *others]

    def engine(self, hooks: HookRegistry | None = None) -> RoundEngine:
        return RoundEngine(postgres_unit_of_work(self.pool), clock=self.clock, hooks=hooks)

    async def submit(self, room_id: uuid.UUID, number: int, users: list[uuid.UUID]) -> None:
        async with self.pool.connection() as connection:
            for user in users:
                await connection.execute(
                    "INSERT INTO public.round_participation (room_id, round_number, user_id)"
                    " VALUES (%s, %s, %s)",
                    (room_id, number, user),
                )

    async def status(self, room_id: uuid.UUID) -> RoomStatus:
        async with self.pool.connection() as connection:
            cursor = await connection.execute(
                "SELECT status FROM public.rooms WHERE id = %s", (room_id,)
            )
            row = await cursor.fetchone()
        assert row is not None
        return RoomStatus(row[0])

    async def jobs(self, room_id: uuid.UUID, task: str) -> int:
        async with self.pool.connection() as connection:
            cursor = await connection.execute(
                "SELECT count(*) FROM procrastinate_jobs"
                " WHERE task_name = %s AND args->>'room_id' = %s",
                (task, str(room_id)),
            )
            row = await cursor.fetchone()
        return int(row[0]) if row else 0  # pyright: ignore[reportArgumentType]

    async def run_worker(self) -> None:
        connector = PsycopgConnector(conninfo=self.database_url)
        with jobs_app.replace_connector(connector):
            async with jobs_app.open_async():
                for _ in range(10):  # each pass runs every job that is due
                    await jobs_app.run_worker_async(
                        queues=["rounds"], wait=False, install_signal_handlers=False
                    )

    async def cleanup(self) -> None:
        async with self.pool.connection() as connection:
            await connection.execute(
                "DELETE FROM procrastinate_jobs WHERE args->>'room_id' IN"
                " (SELECT id::text FROM public.rooms WHERE question_id = ANY(%s))",
                (self.questions,),
            )
            await connection.execute("DELETE FROM auth.users WHERE id = ANY(%s)", (self.users,))
            await connection.execute(
                "DELETE FROM public.rooms WHERE question_id = ANY(%s)", (self.questions,)
            )
            await connection.execute(
                "DELETE FROM public.questions WHERE id = ANY(%s)", (self.questions,)
            )


@pytest.fixture
async def world(database_url: str) -> AsyncGenerator[World]:
    async with create_pool(database_url, max_size=8) as pool:
        fixture = World(pool, database_url)
        resources.use(pool=pool, clock=fixture.clock, hooks=HookRegistry())
        yield fixture
        await fixture.cleanup()


async def test_room_runs_to_finished_through_the_worker(world: World) -> None:
    room_id, members = await world.room(members=3)
    rooms = PostgresRoomRepository(world.pool, clock=world.clock)
    await rooms.start(room_id, min_members=3, max_members=6)
    await world.submit(room_id, 1, members)

    await world.run_worker()

    assert await world.status(room_id) is RoomStatus.FINISHED
    assert await world.jobs(room_id, "archive_room") == 1
    async with world.pool.connection() as connection:
        cursor = await connection.execute(
            "SELECT number, closed_at IS NOT NULL FROM public.rounds"
            " WHERE room_id = %s ORDER BY number",
            (room_id,),
        )
        assert await cursor.fetchall() == [(1, True), (2, True), (3, True)]


async def test_round_one_without_enough_submissions_aborts(world: World) -> None:
    room_id, members = await world.room(members=4)
    await world.engine().start(room_id)
    await world.submit(room_id, 1, members[:2])

    await world.run_worker()

    assert await world.status(room_id) is RoomStatus.ABORTED


async def test_repeated_close_job_has_one_effect(world: World) -> None:
    room_id, members = await world.room(members=3)
    engine = world.engine()
    await engine.start(room_id)
    await world.submit(room_id, 1, members)

    await engine.close_round(room_id, 1)
    await engine.close_round(room_id, 1)

    assert await world.status(room_id) is RoomStatus.R1_CLOSED
    assert await world.jobs(room_id, "after_status") == 1


async def test_concurrent_closes_make_exactly_one_transition(world: World) -> None:
    room_id, members = await world.room(members=3)
    await world.engine().start(room_id)
    await world.submit(room_id, 1, members)

    results = await asyncio.gather(*(world.engine().close_round(room_id, 1) for _ in range(5)))

    assert set(results) == {RoomStatus.R1_CLOSED}
    assert await world.jobs(room_id, "after_status") == 1


async def test_everyone_submitted_closes_early(world: World) -> None:
    room_id, members = await world.room(members=3)
    world.clock.now_value = datetime.now(UTC)  # deadline one hour ahead
    engine = world.engine()
    await engine.start(room_id)

    await world.submit(room_id, 1, members[:2])
    assert await engine.close_if_complete(room_id, 1) is RoomStatus.R1_OPEN
    await world.submit(room_id, 1, members[2:])
    assert await engine.close_if_complete(room_id, 1) is RoomStatus.R1_CLOSED


async def test_status_reader_counts_submissions(world: World) -> None:
    room_id, members = await world.room(members=4)
    world.clock.now_value = datetime.now(UTC)
    await world.engine().start(room_id)
    await world.submit(room_id, 1, members[:2])
    reader = PostgresRoundStatusReader(world.pool)

    mine = await reader.status(room_id, members[0])
    other = await reader.status(room_id, members[3])

    assert mine.status == "R1_OPEN"
    assert mine.round_number == 1
    assert mine.deadline_at is not None
    assert mine.submitted is True
    assert other.submitted is False
    assert mine.submission_count == 2
    assert mine.member_count == 4


async def test_old_forming_rooms_expire(world: World) -> None:
    room_id, _ = await world.room(members=2)
    async with world.pool.connection() as connection:
        await connection.execute(
            "UPDATE public.rooms SET created_at = now() - interval '8 days' WHERE id = %s",
            (room_id,),
        )
    world.clock.now_value = datetime.now(UTC)

    assert await world.engine().expire_forming_rooms() >= 1
    assert await world.status(room_id) is RoomStatus.ABORTED
