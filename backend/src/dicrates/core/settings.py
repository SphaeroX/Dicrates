"""Typed application settings, loaded from environment variables and the root `.env`."""

from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[4] / ".env"
PRODUCTION_LLM_PROVIDER = "mistral"


class AppEnv(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class LlmModel(BaseModel):
    """A Pydantic AI model string `<provider>:<model>`, split into its parts."""

    model_config = ConfigDict(frozen=True)

    provider: str
    model: str

    @classmethod
    def parse(cls, value: str) -> Self:
        provider, separator, model = value.strip().partition(":")
        if not separator or not provider or not model:
            msg = f"LLM_MODEL must look like '<provider>:<model>', got {value!r}"
            raise ValueError(msg)
        return cls(provider=provider, model=model)

    def __str__(self) -> str:
        return f"{self.provider}:{self.model}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: AppEnv = AppEnv.DEVELOPMENT
    llm_model: Annotated[LlmModel, NoDecode] = LlmModel(
        provider="mistral", model="mistral-large-latest"
    )

    #: Days after FINISHED until a room is archived (deletion periods: Task 22).
    archive_after_days: int = 30

    # Provider-standard key names; only the key of the LLM_MODEL provider is needed.
    mistral_api_key: SecretStr | None = None
    google_api_key: SecretStr | None = None

    # Optional until the tasks that need them (database, auth).
    supabase_url: str | None = None
    supabase_anon_key: SecretStr | None = None
    supabase_service_role_key: SecretStr | None = None
    database_url: SecretStr | None = None

    @field_validator("llm_model", mode="before")
    @classmethod
    def _parse_llm_model(cls, value: object) -> object:
        if isinstance(value, str):
            return LlmModel.parse(value)
        return value

    @field_validator(
        "supabase_url",
        "supabase_anon_key",
        "supabase_service_role_key",
        "database_url",
        "mistral_api_key",
        "google_api_key",
        mode="before",
    )
    @classmethod
    def _empty_to_none(cls, value: object) -> object:
        # `.env.example` ships empty values; treat them as unset.
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @model_validator(mode="after")
    def _production_requires_mistral(self) -> Self:
        if self.app_env is AppEnv.PRODUCTION and self.llm_model.provider != PRODUCTION_LLM_PROVIDER:
            msg = (
                f"APP_ENV=production requires a '{PRODUCTION_LLM_PROVIDER}:' LLM_MODEL "
                f"(EU processing), got {self.llm_model}"
            )
            raise ValueError(msg)
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
