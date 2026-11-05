"""PostgresLlmCallLog against the local Supabase stack."""

import uuid

import psycopg
import pytest

from dicrates.core.db import create_pool
from dicrates.llm.call_log import LlmCallRecord, PostgresLlmCallLog

pytestmark = pytest.mark.integration

# Exactly these columns: any new column must be reviewed for text content (GDPR Art. 9).
EXPECTED_COLUMNS = {
    "id",
    "created_at",
    "task",
    "prompt_version",
    "model",
    "input_tokens",
    "output_tokens",
    "duration_ms",
    "success",
    "error_kind",
    "attempts",
    "room_id",
}


async def test_record_is_stored(database_url: str) -> None:
    task = f"test-{uuid.uuid4().hex[:8]}"
    entry = LlmCallRecord(
        task=task,
        prompt_version="demo.v1",
        model="fake:fake-model",
        input_tokens=12,
        output_tokens=3,
        duration_ms=42,
        success=False,
        error_kind="unavailable",
        attempts=2,
        room_id=None,
    )

    async with create_pool(database_url, max_size=2) as pool:
        await PostgresLlmCallLog(pool).record(entry)
        async with pool.connection() as connection:
            cursor = await connection.execute(
                "SELECT prompt_version, input_tokens, output_tokens, success, error_kind, attempts"
                " FROM public.llm_calls WHERE task = %s",
                (task,),
            )
            row = await cursor.fetchone()
            await connection.execute("DELETE FROM public.llm_calls WHERE task = %s", (task,))

    assert row == ("demo.v1", 12, 3, False, "unavailable", 2)


async def test_table_has_no_text_columns(
    db_connection: psycopg.AsyncConnection[tuple[object, ...]],
) -> None:
    cursor = await db_connection.execute(
        "SELECT column_name FROM information_schema.columns"
        " WHERE table_schema = 'public' AND table_name = 'llm_calls'"
    )
    columns = {str(row[0]) for row in await cursor.fetchall()}

    assert columns == EXPECTED_COLUMNS
