from typing import Annotated

from fastapi import Depends
from psycopg_pool import AsyncConnectionPool

from dicrates.core.db import get_db_pool
from dicrates.rounds.status import PostgresRoundStatusReader, RoundStatusReader


def get_round_status_reader(
    pool: Annotated[AsyncConnectionPool, Depends(get_db_pool)],
) -> RoundStatusReader:
    return PostgresRoundStatusReader(pool)


StatusReader = Annotated[RoundStatusReader, Depends(get_round_status_reader)]
