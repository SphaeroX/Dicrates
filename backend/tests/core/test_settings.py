import pytest
from pydantic import ValidationError

from dicrates.core.settings import AppEnv, Settings

ENV_VARS = [
    "LLM_MODEL",
    "APP_ENV",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "DATABASE_URL",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def make_settings() -> Settings:
    # _env_file=None: never read the real .env in tests.
    return Settings(_env_file=None)  # pyright: ignore[reportCallIssue]


def test_defaults_to_development_and_mistral() -> None:
    settings = make_settings()

    assert settings.app_env is AppEnv.DEVELOPMENT
    assert settings.llm_model.provider == "mistral"
    assert settings.llm_model.model == "mistral-large-latest"


def test_llm_model_is_split_into_provider_and_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "mistral:mistral-large-latest")

    settings = make_settings()

    assert settings.llm_model.provider == "mistral"
    assert settings.llm_model.model == "mistral-large-latest"
    assert str(settings.llm_model) == "mistral:mistral-large-latest"


@pytest.mark.parametrize("value", ["mistral-large-latest", "mistral:", ":model", ""])
def test_invalid_llm_model_is_rejected(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("LLM_MODEL", value)

    with pytest.raises(ValidationError):
        make_settings()


def test_production_rejects_non_mistral_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("LLM_MODEL", "google:gemini-3.8-flash")

    with pytest.raises(ValidationError, match="mistral"):
        make_settings()


def test_production_accepts_mistral_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("LLM_MODEL", "mistral:mistral-large-latest")

    settings = make_settings()

    assert settings.app_env is AppEnv.PRODUCTION


@pytest.mark.parametrize("value", ["google:gemini-3.8-flash", "mistral:mistral-small-latest"])
def test_development_accepts_any_provider(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("LLM_MODEL", value)

    settings = make_settings()

    assert str(settings.llm_model) == value


def test_unknown_app_env_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "staging-ish")

    with pytest.raises(ValidationError):
        make_settings()


def test_supabase_and_database_are_optional() -> None:
    settings = make_settings()

    assert settings.supabase_url is None
    assert settings.supabase_anon_key is None
    assert settings.supabase_service_role_key is None
    assert settings.database_url is None


def test_secrets_are_not_shown_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "super-secret-value")

    settings = make_settings()

    assert "super-secret-value" not in repr(settings)
