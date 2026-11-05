from typing import Annotated

from fastapi import Depends, HTTPException, status
from psycopg_pool import AsyncConnectionPool

from dicrates.core.auth import AuthenticatedUser, CurrentUser
from dicrates.core.db import get_db_pool
from dicrates.profiles.repository import PostgresProfileRepository, ProfileRepository


def get_profile_repository(
    pool: Annotated[AsyncConnectionPool, Depends(get_db_pool)],
) -> ProfileRepository:
    return PostgresProfileRepository(pool)


Profiles = Annotated[ProfileRepository, Depends(get_profile_repository)]


async def require_consent(user: CurrentUser, profiles: Profiles) -> AuthenticatedUser:
    """Dependency for every game endpoint: 403 without a valid consent (18+, current text)."""
    consent = await profiles.latest_consent(user.id)
    if consent is None or not consent.is_valid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="consent_required")
    return user


ConsentedUser = Annotated[AuthenticatedUser, Depends(require_consent)]
