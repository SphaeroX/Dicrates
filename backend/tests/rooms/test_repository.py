"""PostgresRoomRepository against the local Supabase stack."""

import asyncio
import uuid
from collections.abc import AsyncGenerator

import psycopg
import pytest
from psycopg import sql
from psycopg_pool import AsyncConnectionPool
from tests.questions.factories import make_content

from dicrates.core.db import create_pool
from dicrates.core.language import Language
from dicrates.questions.repository import PostgresQuestionRepository
from dicrates.rooms.models import JoinOutcome, NewRoom, RoomStatus, StartOutcome
from dicrates.rooms.repository import InviteCodeTakenError, PostgresRoomRepository

pytestmark = pytest.mark.integration


class Fixture:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self.pool = pool
        self.rooms = PostgresRoomRepository(pool)
        self.users: list[uuid.UUID] = []
        self.question_ids: list[uuid.UUID] = []

    async def user(self) -> uuid.UUID:
        user_id = uuid.uuid4()
        async with self.pool.connection() as connection:
            await connection.execute(
                "INSERT INTO auth.users (id, email) VALUES (%s, %s)",
                (user_id, f"{user_id}@example.test"),
            )
        self.users.append(user_id)
        return user_id

    async def new_room(self, code: str) -> NewRoom:
        question = await PostgresQuestionRepository(self.pool).create(make_content())
        self.question_ids.append(question.id)
        return NewRoom(
            question_id=question.id,
            language=Language.EN,
            round_duration_hours=24,
            invite_code=code,
        )

    async def cleanup(self) -> None:
        async with self.pool.connection() as connection:
            await connection.execute("DELETE FROM auth.users WHERE id = ANY(%s)", (self.users,))
            await connection.execute(
                "DELETE FROM public.rooms WHERE question_id = ANY(%s)", (self.question_ids,)
            )
            await connection.execute(
                "DELETE FROM public.questions WHERE id = ANY(%s)", (self.question_ids,)
            )


@pytest.fixture
async def world(database_url: str) -> AsyncGenerator[Fixture]:
    async with create_pool(database_url, max_size=8) as pool:
        fixture = Fixture(pool)
        yield fixture
        await fixture.cleanup()


def code() -> str:
    alphabet = "ABCDEFGHJKMNPQRTUVWXYZ2346789"
    return "".join(alphabet[byte % len(alphabet)] for byte in uuid.uuid4().bytes[:6])


async def test_create_join_start(world: Fixture) -> None:
    creator = await world.user()
    room = await world.rooms.create(await world.new_room(code()), creator_id=creator)
    members = [await world.user(), await world.user()]

    outcomes = [await world.rooms.add_member(room.id, m, max_members=6) for m in members]
    again = await world.rooms.add_member(room.id, members[0], max_members=6)
    started = await world.rooms.start(room.id, min_members=3, max_members=6)

    assert outcomes == [JoinOutcome.ADDED, JoinOutcome.ADDED]
    assert again is JoinOutcome.ALREADY_MEMBER
    assert started is StartOutcome.STARTED
    loaded = await world.rooms.get(room.id)
    assert loaded is not None
    assert loaded.status is RoomStatus.R1_OPEN
    assert loaded.member_count == 3
    assert [r.id for r in await world.rooms.list_for_member(members[1])] == [room.id]


async def test_concurrent_joins_respect_the_limit(world: Fixture) -> None:
    room = await world.rooms.create(await world.new_room(code()), creator_id=await world.user())
    joiners = [await world.user() for _ in range(8)]

    outcomes = await asyncio.gather(
        *(world.rooms.add_member(room.id, user, max_members=6) for user in joiners)
    )

    assert outcomes.count(JoinOutcome.ADDED) == 5
    assert outcomes.count(JoinOutcome.FULL) == 3


async def test_active_invite_codes_are_unique(world: Fixture) -> None:
    shared = code()
    first = await world.rooms.create(await world.new_room(shared), creator_id=await world.user())

    with pytest.raises(InviteCodeTakenError):
        await world.rooms.create(await world.new_room(shared), creator_id=await world.user())

    await world.rooms.dissolve(first.id)
    reused = await world.rooms.create(await world.new_room(shared), creator_id=await world.user())
    assert reused.invite_code == shared
    assert await world.rooms.find_active_by_code(shared) == reused


async def test_leave_and_rejoin(world: Fixture) -> None:
    room = await world.rooms.create(await world.new_room(code()), creator_id=await world.user())
    member = await world.user()
    await world.rooms.add_member(room.id, member, max_members=6)

    assert await world.rooms.remove_member(room.id, member) is True
    assert await world.rooms.is_member(room.id, member) is False
    assert await world.rooms.add_member(room.id, member, max_members=6) is JoinOutcome.ADDED


@pytest.mark.parametrize("role", ["anon", "authenticated"])
@pytest.mark.parametrize("table", ["rooms", "room_members"])
async def test_clients_cannot_read_rooms(
    db_connection: psycopg.AsyncConnection[tuple[object, ...]], role: str, table: str
) -> None:
    await db_connection.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))

    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        await db_connection.execute(
            sql.SQL("SELECT * FROM public.{}").format(sql.Identifier(table))
        )
