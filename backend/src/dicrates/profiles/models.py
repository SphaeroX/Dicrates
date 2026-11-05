import re
import uuid
from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator

from dicrates.profiles.consent import CURRENT_CONSENT_VERSION

PSEUDONYM_MIN_LENGTH = 3
PSEUDONYM_MAX_LENGTH = 24
# Letters (any script) and digits, inner spaces, hyphens and underscores.
_PSEUDONYM_PATTERN = re.compile(r"[^\W_](?:[\w \-]*[^\W_])?")


class Language(StrEnum):
    EN = "en"
    DE = "de"


def _validate_pseudonym(value: str) -> str:
    value = value.strip()
    if not PSEUDONYM_MIN_LENGTH <= len(value) <= PSEUDONYM_MAX_LENGTH:
        msg = f"pseudonym must be {PSEUDONYM_MIN_LENGTH}-{PSEUDONYM_MAX_LENGTH} characters"
        raise ValueError(msg)
    if not _PSEUDONYM_PATTERN.fullmatch(value) or "  " in value:
        msg = "pseudonym may contain letters, digits, single spaces, '-' and '_'"
        raise ValueError(msg)
    return value


Pseudonym = Annotated[str, AfterValidator(_validate_pseudonym)]


class Profile(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: uuid.UUID
    pseudonym: str | None
    language: Language
    created_at: datetime


class ProfileUpdate(BaseModel):
    """PATCH body; only fields that are sent are changed."""

    model_config = ConfigDict(extra="forbid")

    pseudonym: Pseudonym | None = Field(default=None)
    language: Language | None = Field(default=None)

    @field_validator("pseudonym", "language", mode="before")
    @classmethod
    def _reject_explicit_null(cls, value: object) -> object:
        if value is None:
            msg = "field cannot be cleared"
            raise ValueError(msg)
        return value


class Consent(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: uuid.UUID
    consent_version: str
    age_confirmed: bool
    granted_at: datetime

    @property
    def is_valid(self) -> bool:
        return self.age_confirmed and self.consent_version == CURRENT_CONSENT_VERSION
