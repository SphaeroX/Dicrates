"""Runs one LLM task with structured, validated output, retries and a usage record."""

import asyncio
import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.exceptions import (
    ModelAPIError,
    ModelConnectionError,
    ModelHTTPError,
    ModelRateLimitError,
    ModelRequestTimeout,
    ModelServerError,
    ModelUnavailableError,
    UnexpectedModelBehavior,
)
from pydantic_ai.models import Model
from pydantic_ai.usage import RunUsage

from dicrates.llm.call_log import LlmCallLog, LlmCallRecord
from dicrates.llm.prompts import RenderedPrompt

logger = logging.getLogger(__name__)

_TRANSIENT_ERRORS = (
    ModelRateLimitError,
    ModelServerError,
    ModelConnectionError,
    ModelUnavailableError,
    ModelRequestTimeout,
)


class LlmError(Exception):
    """Base class; messages never contain prompt, input or output text."""


class LlmOutputError(LlmError):
    """The model kept returning output that failed schema validation."""


class LlmUnavailableError(LlmError):
    """The provider failed permanently or kept failing transiently."""


@dataclass(frozen=True)
class LlmResult[OutputT: BaseModel]:
    output: OutputT
    prompt_version: str
    model: str
    input_tokens: int
    output_tokens: int


async def exponential_backoff(attempt: int) -> None:
    await asyncio.sleep(min(2**attempt, 30))


def _is_transient(error: ModelAPIError) -> bool:
    if isinstance(error, _TRANSIENT_ERRORS):
        return True
    return isinstance(error, ModelHTTPError) and (
        error.status_code == 429 or error.status_code >= 500
    )


class LlmRunner:
    def __init__(
        self,
        model: Model,
        *,
        model_id: str,
        call_log: LlmCallLog,
        output_retries: int = 2,
        transient_retries: int = 3,
        backoff: Callable[[int], Awaitable[None]] = exponential_backoff,
    ) -> None:
        self._model = model
        self._model_id = model_id
        self._call_log = call_log
        self._output_retries = output_retries
        self._transient_retries = transient_retries
        self._backoff = backoff

    async def run[OutputT: BaseModel](
        self,
        *,
        task: str,
        prompt: RenderedPrompt,
        output_type: type[OutputT],
        user_input: str,
        room_id: uuid.UUID | None = None,
    ) -> LlmResult[OutputT]:
        """Run `prompt` (instructions) on `user_input` and return validated `output_type`."""
        agent = Agent(
            self._model,
            output_type=output_type,
            instructions=prompt.text,
            retries={"output": self._output_retries},
        )
        usage = RunUsage()
        started = time.monotonic()
        attempts = 0
        error_kind: str | None = None
        try:
            while True:
                attempts += 1
                try:
                    result = await agent.run(user_input, usage=usage)
                except ModelAPIError as error:
                    if _is_transient(error) and attempts <= self._transient_retries:
                        await self._backoff(attempts)
                        continue
                    error_kind = "unavailable"
                    raise LlmUnavailableError(type(error).__name__) from None
                except UnexpectedModelBehavior:
                    error_kind = "output_invalid"
                    raise LlmOutputError(task) from None
                return LlmResult(
                    output=result.output,
                    prompt_version=prompt.version,
                    model=self._model_id,
                    input_tokens=usage.input_tokens,
                    output_tokens=usage.output_tokens,
                )
        finally:
            await self._record(
                task=task,
                prompt=prompt,
                usage=usage,
                started=started,
                attempts=attempts,
                error_kind=error_kind,
                room_id=room_id,
            )

    async def _record(
        self,
        *,
        task: str,
        prompt: RenderedPrompt,
        usage: RunUsage,
        started: float,
        attempts: int,
        error_kind: str | None,
        room_id: uuid.UUID | None,
    ) -> None:
        entry = LlmCallRecord(
            task=task,
            prompt_version=prompt.version,
            model=self._model_id,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            duration_ms=int((time.monotonic() - started) * 1000),
            success=error_kind is None,
            error_kind=error_kind,
            attempts=attempts,
            room_id=room_id,
        )
        try:
            await self._call_log.record(entry)
        except Exception:
            # The usage log must never break a game step; the entry has no text.
            logger.exception("could not write LLM usage record for task %s", task)
