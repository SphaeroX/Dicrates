import uuid
from typing import Protocol

from psycopg.rows import class_row
from psycopg_pool import AsyncConnectionPool

from dicrates.profiles.models import Consent, Profile, ProfileUpdate


class ProfileRepository(Protocol):
    async def get_or_create(self, user_id: uuid.UUID) -> Profile: ...

    async def update(self, user_id: uuid.UUID, changes: ProfileUpdate) -> Profile: ...

    async def add_consent(
        self, user_id: uuid.UUID, *, consent_version: str, age_confirmed: bool
    ) -> Consent: ...

    async def latest_consent(self, user_id: uuid.UUID) -> Consent | None: ...


class PostgresProfileRepository:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._pool = pool

    async def get_or_create(self, user_id: uuid.UUID) -> Profile:
        async with self._pool.connection() as connection:
            await connection.execute(
                "INSERT INTO public.profiles (id) VALUES (%s) ON CONFLICT (id) DO NOTHING",
                (user_id,),
            )
            cursor = connection.cursor(row_factory=class_row(Profile))
            await cursor.execute(
                "SELECT id, pseudonym, language, created_at FROM public.profiles WHERE id = %s",
                (user_id,),
            )
            profile = await cursor.fetchone()
        if profile is None:  # pragma: no cover - the row was just inserted
            msg = "profile vanished"
            raise RuntimeError(msg)
        return profile

    async def update(self, user_id: uuid.UUID, changes: ProfileUpdate) -> Profile:
        await self.get_or_create(user_id)
        values = changes.model_dump(exclude_unset=True)
        if not values:
            return await self.get_or_create(user_id)
        async with self._pool.connection() as connection:
            cursor = connection.cursor(row_factory=class_row(Profile))
            await cursor.execute(
                "UPDATE public.profiles SET"
                " pseudonym = CASE WHEN %(set_pseudonym)s THEN %(pseudonym)s ELSE pseudonym END,"
                " language = CASE WHEN %(set_language)s THEN %(language)s ELSE language END"
                " WHERE id = %(id)s RETURNING id, pseudonym, language, created_at",
                {
                    "id": user_id,
                    "set_pseudonym": "pseudonym" in values,
                    "pseudonym": values.get("pseudonym"),
                    "set_language": "language" in values,
                    "language": values.get("language"),
                },
            )
            profile = await cursor.fetchone()
        if profile is None:  # pragma: no cover
            msg = "profile vanished"
            raise RuntimeError(msg)
        return profile

    async def add_consent(
        self, user_id: uuid.UUID, *, consent_version: str, age_confirmed: bool
    ) -> Consent:
        async with self._pool.connection() as connection:
            cursor = connection.cursor(row_factory=class_row(Consent))
            await cursor.execute(
                "INSERT INTO public.consents (user_id, consent_version, age_confirmed)"
                " VALUES (%s, %s, %s)"
                " RETURNING user_id, consent_version, age_confirmed, granted_at",
                (user_id, consent_version, age_confirmed),
            )
            consent = await cursor.fetchone()
        if consent is None:  # pragma: no cover
            msg = "consent insert returned nothing"
            raise RuntimeError(msg)
        return consent

    async def latest_consent(self, user_id: uuid.UUID) -> Consent | None:
        async with self._pool.connection() as connection:
            cursor = connection.cursor(row_factory=class_row(Consent))
            await cursor.execute(
                "SELECT user_id, consent_version, age_confirmed, granted_at"
                " FROM public.consents WHERE user_id = %s"
                " ORDER BY granted_at DESC, id DESC LIMIT 1",
                (user_id,),
            )
            return await cursor.fetchone()
