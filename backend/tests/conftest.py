"""Shared fixtures. Integration tests need the local Supabase stack (`npx supabase start`).

Without a reachable database, `integration` tests are skipped locally. CI sets
`DICRATES_REQUIRE_DB=1`, which turns an unreachable database into a failure.
"""

import asyncio
import os
import selectors
import sys
from collections.abc import AsyncIterator, Callable, Mapping
from functools import cache

import psycopg
import pytest

LOCAL_DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"

type Connection = psycopg.AsyncConnection[tuple[object, ...]]


def integration_database_url() -> str:
    return os.environ.get("TEST_DATABASE_URL", LOCAL_DATABASE_URL)


@cache
def database_unreachable_reason() -> str | None:
    try:
        psycopg.connect(integration_database_url(), connect_timeout=2).close()
    except psycopg.OperationalError as error:
        return (
            f"local database not reachable ({error.__class__.__name__}); run `npx supabase start`"
        )
    return None


def pytest_runtest_setup(item: pytest.Item) -> None:
    if item.get_closest_marker("integration") is None:
        return
    reason = database_unreachable_reason()
    if reason is None:
        return
    if os.environ.get("DICRATES_REQUIRE_DB") == "1":
        pytest.fail(reason)
    pytest.skip(reason)


if sys.platform == "win32":
    # psycopg async cannot run on Windows' default ProactorEventLoop. The hook must
    # return a non-empty mapping, so it is only defined on Windows.
    def pytest_asyncio_loop_factories(
        config: pytest.Config, item: pytest.Item
    ) -> Mapping[str, Callable[[], asyncio.AbstractEventLoop]]:
        return {"selector": lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())}


@pytest.fixture
def database_url() -> str:
    return integration_database_url()


@pytest.fixture
async def db_connection(database_url: str) -> AsyncIterator[Connection]:
    """A connection inside a transaction that is rolled back after the test."""
    connection = await psycopg.AsyncConnection.connect(database_url)
    try:
        yield connection
    finally:
        await connection.rollback()
        await connection.close()
