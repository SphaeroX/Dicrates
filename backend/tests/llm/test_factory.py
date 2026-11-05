import pytest
from pydantic import SecretStr
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.mistral import MistralModel

from dicrates.core.settings import LlmModel, Settings
from dicrates.llm.factory import LlmConfigurationError, build_model


def settings_with(model: str, **keys: str) -> Settings:
    return Settings(
        _env_file=None,  # pyright: ignore[reportCallIssue]
        llm_model=LlmModel.parse(model),
        **{name: SecretStr(value) for name, value in keys.items()},
    )


def test_builds_mistral_model() -> None:
    model = build_model(settings_with("mistral:mistral-large-latest", mistral_api_key="test-key"))

    assert isinstance(model, MistralModel)
    assert model.model_name == "mistral-large-latest"


def test_builds_google_model() -> None:
    model = build_model(settings_with("google:gemini-3.8-flash", google_api_key="test-key"))

    assert isinstance(model, GoogleModel)
    assert model.model_name == "gemini-3.8-flash"


def test_unknown_provider_is_rejected() -> None:
    with pytest.raises(LlmConfigurationError, match="openai"):
        build_model(settings_with("openai:gpt-9"))


@pytest.mark.parametrize("model", ["mistral:mistral-large-latest", "google:gemini-3.8-flash"])
def test_missing_api_key_is_rejected(model: str) -> None:
    with pytest.raises(LlmConfigurationError, match="API_KEY"):
        build_model(settings_with(model))
