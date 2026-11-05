"""PostgresProfileRepository against the local Supabase stack."""

import uuid
from collections.abc import AsyncIterator

import pytest
from psycopg_pool import AsyncConnectionPool

from dicrates.core.db import create_pool
from dicrates.profiles.models import Language, ProfileUpdate
from dicrates.profiles.repository import PostgresProfileRepository

pytestmark = pytest.mark.integration


@pytest.fixture
async def pool(database_url: str) -> AsyncIterator[AsyncConnectionPool]:
    async with create_pool(database_url, min_size=1, max_size=2) as pool:
        yield pool


@pytest.fixture
async def user_id(pool: AsyncConnectionPool) -> AsyncIterator[uuid.UUID]:
    user_id = uuid.uuid4()
    async with pool.connection() as connection:
        await connection.execute(
            "INSERT INTO auth.users (id, email) VALUES (%s, %s)",
            (user_id, f"{user_id}@example.test"),
        )
    yield user_id
    async with pool.connection() as connection:
        await connection.execute("DELETE FROM auth.users WHERE id = %s", (user_id,))


async def test_get_or_create_creates_once(pool: AsyncConnectionPool, user_id: uuid.UUID) -> None:
    repository = PostgresProfileRepository(pool)

    first = await repository.get_or_create(user_id)
    second = await repository.get_or_create(user_id)

    assert first == second
    assert first.pseudonym is None
    assert first.language is Language.EN


async def test_update_changes_only_given_fields(
    pool: AsyncConnectionPool, user_id: uuid.UUID
) -> None:
    repository = PostgresProfileRepository(pool)
    await repository.update(user_id, ProfileUpdate(language=Language.DE))

    profile = await repository.update(user_id, ProfileUpdate(pseudonym="Owl"))

    assert profile.pseudonym == "Owl"
    assert profile.language is Language.DE


async def test_latest_consent_returns_newest(pool: AsyncConnectionPool, user_id: uuid.UUID) -> None:
    repository = PostgresProfileRepository(pool)
    assert await repository.latest_consent(user_id) is None

    await repository.add_consent(user_id, consent_version="0", age_confirmed=True)
    await repository.add_consent(user_id, consent_version="1", age_confirmed=True)

    latest = await repository.latest_consent(user_id)
    assert latest is not None
    assert latest.consent_version == "1"
    assert latest.age_confirmed is True


async def test_deleting_the_user_removes_profile_and_consents(
    pool: AsyncConnectionPool, user_id: uuid.UUID
) -> None:
    repository = PostgresProfileRepository(pool)
    await repository.add_consent(user_id, consent_version="1", age_confirmed=True)

    async with pool.connection() as connection:
        await connection.execute("DELETE FROM auth.users WHERE id = %s", (user_id,))
        cursor = await connection.execute(
            "SELECT (SELECT count(*) FROM public.profiles WHERE id = %s)"
            " + (SELECT count(*) FROM public.consents WHERE user_id = %s)",
            (user_id, user_id),
        )
        assert await cursor.fetchone() == (0,)
