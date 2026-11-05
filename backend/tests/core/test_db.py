import psycopg
import pytest

from dicrates.core.db import create_pool


@pytest.mark.integration
async def test_pool_runs_a_query(database_url: str) -> None:
    async with create_pool(database_url) as pool, pool.connection() as connection:
        cursor = await connection.execute("SELECT 1 + 1")
        row = await cursor.fetchone()

    assert row == (2,)


@pytest.mark.integration
async def test_migrations_created_profiles_table(
    db_connection: psycopg.AsyncConnection[tuple[object, ...]],
) -> None:
    cursor = await db_connection.execute("SELECT to_regclass('public.profiles') IS NOT NULL")

    assert await cursor.fetchone() == (True,)
