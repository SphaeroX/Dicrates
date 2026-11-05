from typing import Annotated

from fastapi import Depends
from psycopg_pool import AsyncConnectionPool

from dicrates.core.db import get_db_pool
from dicrates.rooms.repository import PostgresRoomRepository, RoomRepository


def get_room_repository(
    pool: Annotated[AsyncConnectionPool, Depends(get_db_pool)],
) -> RoomRepository:
    return PostgresRoomRepository(pool)


Rooms = Annotated[RoomRepository, Depends(get_room_repository)]
