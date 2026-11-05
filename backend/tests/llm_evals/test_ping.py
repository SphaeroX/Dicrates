"""Real-LLM checks. Run only on request: `uv run pytest -m llm -k ping`.

Uses the configured `LLM_MODEL` and its key from the root `.env`. With a
`google:` (Gemini) model, send invented text only - never real user data.
"""

import pytest
from pydantic import BaseModel
from pydantic_ai import models
from tests.llm.fakes import InMemoryLlmCallLog

from dicrates.core.settings import Settings
from dicrates.llm.factory import build_model
from dicrates.llm.prompts import default_registry
from dicrates.llm.runner import LlmRunner

pytestmark = pytest.mark.llm


class PingReply(BaseModel):
    reply: str
    language: str


@pytest.fixture
def allow_model_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(models, "ALLOW_MODEL_REQUESTS", True)


@pytest.mark.usefixtures("allow_model_requests")
async def test_ping_configured_model() -> None:
    settings = Settings()
    log = InMemoryLlmCallLog()
    runner = LlmRunner(build_model(settings), model_id=str(settings.llm_model), call_log=log)
    prompt = default_registry().load("ping", version=1).render(language="German")

    result = await runner.run(
        task="ping",
        prompt=prompt,
        output_type=PingReply,
        user_input="Hello from an invented test user. This is a connectivity check.",
    )

    print(f"\nLLM ping via {result.model}: {result.output!r}")
    assert result.output.reply
    assert result.output.language.lower().startswith("de")
    assert log.records[-1].success is True
    assert log.records[-1].input_tokens > 0
