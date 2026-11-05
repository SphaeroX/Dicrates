"""Usage log of LLM calls (`llm_calls` table): counts and timings, never any text.

No prompt, no user input and no model output is stored or logged here: they can
contain political opinions (GDPR Art. 9).
"""

import uuid
from dataclasses import dataclass
from typing import Protocol

from psycopg_pool import AsyncConnectionPool


@dataclass(frozen=True)
class LlmCallRecord:
    task: str
    prompt_version: str
    model: str
    input_tokens: int
    output_tokens: int
    duration_ms: int
    success: bool
    #: Short category such as `output_invalid` or `unavailable`; never a message.
    error_kind: str | None
    attempts: int
    room_id: uuid.UUID | None


class LlmCallLog(Protocol):
    async def record(self, entry: LlmCallRecord) -> None: ...


class PostgresLlmCallLog:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._pool = pool

    async def record(self, entry: LlmCallRecord) -> None:
        async with self._pool.connection() as connection:
            await connection.execute(
                "INSERT INTO public.llm_calls (task, prompt_version, model, input_tokens,"
                " output_tokens, duration_ms, success, error_kind, attempts, room_id)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    entry.task,
                    entry.prompt_version,
                    entry.model,
                    entry.input_tokens,
                    entry.output_tokens,
                    entry.duration_ms,
                    entry.success,
                    entry.error_kind,
                    entry.attempts,
                    entry.room_id,
                ),
            )
