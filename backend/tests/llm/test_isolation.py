"""Guards for the LLM layer rules in docs/architecture.md."""

import ast
from pathlib import Path

import pytest
from pydantic import BaseModel, SecretStr
from pydantic_ai import Agent

from dicrates.core.settings import LlmModel, Settings
from dicrates.llm.factory import build_model

SRC = Path(__file__).resolve().parents[2] / "src" / "dicrates"
PROVIDER_MODULES = (
    "pydantic_ai.models.mistral",
    "pydantic_ai.models.google",
    "pydantic_ai.providers",
    "mistralai",
    "google.genai",
    "openai",
    "anthropic",
)


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_only_the_llm_factory_imports_provider_code() -> None:
    offenders = [
        f"{path.relative_to(SRC)}: {module}"
        for path in SRC.rglob("*.py")
        if path != SRC / "llm" / "factory.py"
        for module in imported_modules(path)
        if module.startswith(PROVIDER_MODULES)
    ]

    assert offenders == []


def test_no_llm_telemetry_is_configured() -> None:
    offenders = [
        str(path.relative_to(SRC))
        for path in SRC.rglob("*.py")
        if any(module.startswith("logfire") for module in imported_modules(path))
    ]

    assert offenders == []


class Answer(BaseModel):
    text: str


async def test_real_model_requests_are_blocked_in_the_test_suite() -> None:
    settings = Settings(
        _env_file=None,  # pyright: ignore[reportCallIssue]
        llm_model=LlmModel.parse("mistral:mistral-large-latest"),
        mistral_api_key=SecretStr("not-a-real-key"),
    )
    agent = Agent(build_model(settings), output_type=Answer)

    with pytest.raises(RuntimeError, match="ALLOW_MODEL_REQUESTS"):
        await agent.run("hello")
