"""Postgres access: psycopg 3 async with a connection pool, plain SQL."""

from psycopg_pool import AsyncConnectionPool


def create_pool(conninfo: str, *, min_size: int = 1, max_size: int = 10) -> AsyncConnectionPool:
    """Create an unopened pool; open it with `async with` or `await pool.open()`."""
    return AsyncConnectionPool(conninfo, min_size=min_size, max_size=max_size, open=False)
