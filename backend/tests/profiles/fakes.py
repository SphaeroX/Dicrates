import uuid
from datetime import UTC, datetime

from dicrates.profiles.models import Consent, Language, Profile, ProfileUpdate


class FakeProfileRepository:
    """In-memory `ProfileRepository` for unit tests."""

    def __init__(self) -> None:
        self.profiles: dict[uuid.UUID, Profile] = {}
        self.consents: list[Consent] = []

    async def get_or_create(self, user_id: uuid.UUID) -> Profile:
        if user_id not in self.profiles:
            self.profiles[user_id] = Profile(
                id=user_id, pseudonym=None, language=Language.EN, created_at=datetime.now(UTC)
            )
        return self.profiles[user_id]

    async def update(self, user_id: uuid.UUID, changes: ProfileUpdate) -> Profile:
        profile = await self.get_or_create(user_id)
        updated = profile.model_copy(update=changes.model_dump(exclude_unset=True))
        self.profiles[user_id] = updated
        return updated

    async def add_consent(
        self, user_id: uuid.UUID, *, consent_version: str, age_confirmed: bool
    ) -> Consent:
        await self.get_or_create(user_id)
        consent = Consent(
            user_id=user_id,
            consent_version=consent_version,
            age_confirmed=age_confirmed,
            granted_at=datetime.now(UTC),
        )
        self.consents.append(consent)
        return consent

    async def latest_consent(self, user_id: uuid.UUID) -> Consent | None:
        own = [consent for consent in self.consents if consent.user_id == user_id]
        return own[-1] if own else None
