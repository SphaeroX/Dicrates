"""Procrastinate jobs that drive rooms through the rounds. They take only ids."""

import uuid
from datetime import timedelta

from procrastinate import RetryStrategy

from dicrates.jobs.app import app
from dicrates.jobs.resources import resources
from dicrates.rooms.models import RoomStatus
from dicrates.rounds.engine import RoundEngine
from dicrates.rounds.postgres import postgres_unit_of_work

#: After this long without progress a job is retried (e.g. LLM step failed).
RETRY = RetryStrategy(max_attempts=5, wait=60, exponential_wait=2)


async def engine() -> RoundEngine:
    pool = await resources.pool()
    return RoundEngine(
        postgres_unit_of_work(pool),
        clock=resources.clock,
        hooks=resources.hooks,
        archive_after=timedelta(days=resources.settings().archive_after_days),
    )


@app.task(name="close_round", queue="rounds", retry=RETRY)
async def close_round(room_id: str, round_number: int) -> None:
    await (await engine()).close_round(uuid.UUID(room_id), round_number)


@app.task(name="after_status", queue="rounds", retry=RETRY)
async def after_status(room_id: str, status: str) -> None:
    await (await engine()).after_status(uuid.UUID(room_id), RoomStatus(status))


@app.task(name="archive_room", queue="rounds", retry=RETRY)
async def archive_room(room_id: str) -> None:
    await (await engine()).archive(uuid.UUID(room_id))


@app.periodic(cron="23 3 * * *")
@app.task(name="expire_forming_rooms", queue="rounds", queueing_lock="expire_forming_rooms")
async def expire_forming_rooms(timestamp: int) -> None:
    del timestamp
    await (await engine()).expire_forming_rooms()
