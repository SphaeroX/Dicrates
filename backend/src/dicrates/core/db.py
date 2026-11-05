"""Postgres access: psycopg 3 async with a connection pool, plain SQL."""

from fastapi import HTTPException, Request, status
from psycopg_pool import AsyncConnectionPool


def create_pool(conninfo: str, *, min_size: int = 1, max_size: int = 10) -> AsyncConnectionPool:
    """Create an unopened pool; open it with `async with` or `await pool.open()`."""
    return AsyncConnectionPool(conninfo, min_size=min_size, max_size=max_size, open=False)


def get_db_pool(request: Request) -> AsyncConnectionPool:
    """FastAPI dependency: the pool opened by the app lifespan (503 without a database)."""
    pool: AsyncConnectionPool | None = getattr(request.app.state, "db_pool", None)
    if pool is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="no_database")
    return pool
