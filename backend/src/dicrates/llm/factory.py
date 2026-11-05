"""Builds the Pydantic AI model from `LLM_MODEL`. The only module importing provider code.

Requests go directly to the provider API with our own key: no gateway, no
intermediary, no telemetry (Logfire is never configured).
"""

from pydantic import SecretStr
from pydantic_ai.models import Model
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.mistral import MistralProvider

from dicrates.core.settings import Settings


class LlmConfigurationError(Exception):
    """`LLM_MODEL` names an unsupported provider or its API key is missing."""


def _require_key(key: SecretStr | None, env_name: str) -> str:
    if key is None or not key.get_secret_value():
        msg = f"{env_name} must be set for this LLM_MODEL"
        raise LlmConfigurationError(msg)
    return key.get_secret_value()


def build_model(settings: Settings) -> Model:
    llm_model = settings.llm_model
    match llm_model.provider:
        case "mistral":
            api_key = _require_key(settings.mistral_api_key, "MISTRAL_API_KEY")
            return MistralModel(llm_model.model, provider=MistralProvider(api_key=api_key))
        case "google":
            # Dev-only fallback: never with real user data (not EU-bound).
            api_key = _require_key(settings.google_api_key, "GOOGLE_API_KEY")
            return GoogleModel(llm_model.model, provider=GoogleProvider(api_key=api_key))
        case other:
            msg = f"unsupported LLM provider {other!r} (supported: mistral, google)"
            raise LlmConfigurationError(msg)
