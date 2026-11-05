import dataclasses
import uuid

import pytest
from pydantic import BaseModel
from pydantic_ai.exceptions import ModelHTTPError, ModelRateLimitError
from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from tests.llm.fakes import InMemoryLlmCallLog

from dicrates.llm.call_log import LlmCallRecord
from dicrates.llm.prompts import RenderedPrompt
from dicrates.llm.runner import LlmOutputError, LlmRunner, LlmUnavailableError

INVENTED_OPINION = "My invented opinion: cats should vote."  # must never be logged
PROMPT = RenderedPrompt(version="demo.v1", text="Answer in English.")


class Verdict(BaseModel):
    score: int
    reason: str


def answering(*responses: str) -> tuple[FunctionModel, list[int]]:
    """A model that returns the given JSON strings as output tool calls, one per request."""
    calls: list[int] = []

    def respond(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        calls.append(len(messages))
        args = responses[min(len(calls), len(responses)) - 1]
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, args)])

    return FunctionModel(respond, model_name="fake-model"), calls


def failing(error: Exception, *, times: int, then: str) -> tuple[FunctionModel, list[int]]:
    calls: list[int] = []

    def respond(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        calls.append(1)
        if len(calls) <= times:
            raise error
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, then)])

    return FunctionModel(respond, model_name="fake-model"), calls


async def no_wait(attempt: int) -> None:
    del attempt


def make_runner(model: FunctionModel, log: InMemoryLlmCallLog, **kwargs: int) -> LlmRunner:
    return LlmRunner(model, model_id="fake:fake-model", call_log=log, backoff=no_wait, **kwargs)


VALID = '{"score": 3, "reason": "clear"}'
INVALID = '{"score": "high"}'


async def test_returns_validated_output_with_metadata() -> None:
    log = InMemoryLlmCallLog()
    model, _ = answering(VALID)

    result = await make_runner(model, log).run(
        task="demo", prompt=PROMPT, output_type=Verdict, user_input=INVENTED_OPINION
    )

    assert result.output == Verdict(score=3, reason="clear")
    assert result.prompt_version == "demo.v1"
    assert result.model == "fake:fake-model"
    assert result.input_tokens > 0
    assert result.output_tokens > 0


async def test_retries_after_invalid_output() -> None:
    log = InMemoryLlmCallLog()
    model, calls = answering(INVALID, VALID)

    result = await make_runner(model, log).run(
        task="demo", prompt=PROMPT, output_type=Verdict, user_input=INVENTED_OPINION
    )

    assert result.output.score == 3
    assert len(calls) == 2


async def test_gives_up_after_max_output_retries() -> None:
    log = InMemoryLlmCallLog()
    model, calls = answering(INVALID)

    with pytest.raises(LlmOutputError):
        await make_runner(model, log, output_retries=2).run(
            task="demo", prompt=PROMPT, output_type=Verdict, user_input=INVENTED_OPINION
        )

    assert len(calls) == 3  # first try + 2 retries
    [record] = log.records
    assert record.success is False
    assert record.error_kind == "output_invalid"


async def test_retries_transient_provider_errors() -> None:
    log = InMemoryLlmCallLog()
    model, calls = failing(ModelRateLimitError("fake-model", "slow down"), times=2, then=VALID)

    result = await make_runner(model, log, transient_retries=3).run(
        task="demo", prompt=PROMPT, output_type=Verdict, user_input=INVENTED_OPINION
    )

    assert result.output.score == 3
    assert len(calls) == 3
    assert log.records[-1].attempts == 3


async def test_stops_after_max_transient_retries() -> None:
    log = InMemoryLlmCallLog()
    model, calls = failing(ModelRateLimitError("fake-model", "slow down"), times=99, then=VALID)

    with pytest.raises(LlmUnavailableError):
        await make_runner(model, log, transient_retries=2).run(
            task="demo", prompt=PROMPT, output_type=Verdict, user_input=INVENTED_OPINION
        )

    assert len(calls) == 3
    assert log.records[-1].error_kind == "unavailable"


async def test_does_not_retry_permanent_errors() -> None:
    log = InMemoryLlmCallLog()
    error = ModelHTTPError(status_code=400, model_name="fake-model", body=None)
    model, calls = failing(error, times=99, then=VALID)

    with pytest.raises(LlmUnavailableError):
        await make_runner(model, log, transient_retries=3).run(
            task="demo", prompt=PROMPT, output_type=Verdict, user_input=INVENTED_OPINION
        )

    assert len(calls) == 1


async def test_logs_usage_without_any_text() -> None:
    log = InMemoryLlmCallLog()
    model, _ = answering(VALID)
    room_id = uuid.uuid4()

    await make_runner(model, log).run(
        task="demo",
        prompt=PROMPT,
        output_type=Verdict,
        user_input=INVENTED_OPINION,
        room_id=room_id,
    )

    [record] = log.records
    assert record.task == "demo"
    assert record.prompt_version == "demo.v1"
    assert record.model == "fake:fake-model"
    assert record.success is True
    assert record.room_id == room_id
    assert record.input_tokens > 0
    assert record.output_tokens > 0
    assert record.duration_ms >= 0
    values = " ".join(str(value) for value in dataclasses.asdict(record).values())
    assert INVENTED_OPINION not in values
    assert "clear" not in values  # nothing from the model's answer either
    assert PROMPT.text not in values


def test_call_record_has_no_text_fields() -> None:
    names = {field.name for field in dataclasses.fields(LlmCallRecord)}

    assert names == {
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
