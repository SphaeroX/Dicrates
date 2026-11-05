import uuid
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict, field_validator

from dicrates.core.auth import CurrentUser
from dicrates.profiles.consent import CURRENT_CONSENT_VERSION
from dicrates.profiles.dependencies import Profiles
from dicrates.profiles.models import Consent, Language, Profile, ProfileUpdate

router = APIRouter(prefix="/me", tags=["me"])


class ConsentOut(BaseModel):
    consent_version: str
    age_confirmed: bool
    granted_at: datetime

    @classmethod
    def of(cls, consent: Consent) -> ConsentOut:
        return cls(
            consent_version=consent.consent_version,
            age_confirmed=consent.age_confirmed,
            granted_at=consent.granted_at,
        )


class MeOut(BaseModel):
    id: uuid.UUID
    pseudonym: str | None
    language: Language
    consent: ConsentOut | None
    onboarding_complete: bool
    current_consent_version: str


class ConsentIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    consent_version: str
    # Under-18s cannot consent; the app blocks them before this request.
    age_confirmed: Literal[True]

    @field_validator("consent_version")
    @classmethod
    def _must_be_current(cls, value: str) -> str:
        if value != CURRENT_CONSENT_VERSION:
            msg = f"consent text version {value!r} is outdated"
            raise ValueError(msg)
        return value


def _me(profile: Profile, consent: Consent | None) -> MeOut:
    valid = consent is not None and consent.is_valid
    return MeOut(
        id=profile.id,
        pseudonym=profile.pseudonym,
        language=profile.language,
        consent=ConsentOut.of(consent) if valid and consent else None,
        onboarding_complete=valid and profile.pseudonym is not None,
        current_consent_version=CURRENT_CONSENT_VERSION,
    )


@router.get("")
async def get_me(user: CurrentUser, profiles: Profiles) -> MeOut:
    """The caller's profile; created on the first call after sign-in."""
    profile = await profiles.get_or_create(user.id)
    return _me(profile, await profiles.latest_consent(user.id))


@router.patch("")
async def update_me(user: CurrentUser, profiles: Profiles, changes: ProfileUpdate) -> MeOut:
    profile = await profiles.update(user.id, changes)
    return _me(profile, await profiles.latest_consent(user.id))


@router.post("/consent", status_code=status.HTTP_201_CREATED)
async def give_consent(user: CurrentUser, profiles: Profiles, body: ConsentIn) -> ConsentOut:
    """Store the explicit consent (GDPR Art. 9) and the 18+ confirmation."""
    consent = await profiles.add_consent(
        user.id, consent_version=body.consent_version, age_confirmed=body.age_confirmed
    )
    return ConsentOut.of(consent)
