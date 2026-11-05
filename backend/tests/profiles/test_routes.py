import asyncio
import uuid
from typing import Annotated

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from tests.auth_helpers import TEST_ISSUER, FakeJwksClient, SigningKey
from tests.profiles.fakes import FakeProfileRepository

from dicrates.core.auth import AuthenticatedUser, TokenVerifier, get_token_verifier
from dicrates.core.settings import Settings
from dicrates.main import create_app
from dicrates.profiles.consent import CURRENT_CONSENT_VERSION
from dicrates.profiles.dependencies import get_profile_repository, require_consent


class Api:
    def __init__(self) -> None:
        self.key = SigningKey(kid="key-1")
        self.repository = FakeProfileRepository()
        app = create_app(Settings(_env_file=None))  # pyright: ignore[reportCallIssue]

        @app.get("/test/game")
        def game(  # pyright: ignore[reportUnusedFunction]
            user: Annotated[AuthenticatedUser, Depends(require_consent)],
        ) -> dict[str, str]:
            return {"id": str(user.id)}

        app.dependency_overrides[get_token_verifier] = lambda: TokenVerifier(
            jwks_client=FakeJwksClient(self.key), issuer=TEST_ISSUER
        )
        app.dependency_overrides[get_profile_repository] = lambda: self.repository
        self.client = TestClient(app)

    def headers(self, user_id: uuid.UUID) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.key.token(sub=user_id)}"}


@pytest.fixture
def api() -> Api:
    return Api()


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


def give_consent(api: Api, user_id: uuid.UUID, **overrides: object) -> int:
    body = {"consent_version": CURRENT_CONSENT_VERSION, "age_confirmed": True, **overrides}
    return api.client.post("/me/consent", json=body, headers=api.headers(user_id)).status_code


def test_me_requires_authentication(api: Api) -> None:
    assert api.client.get("/me").status_code == 401


def test_first_get_me_creates_profile(api: Api, user_id: uuid.UUID) -> None:
    response = api.client.get("/me", headers=api.headers(user_id))

    assert response.status_code == 200
    assert response.json() == {
        "id": str(user_id),
        "pseudonym": None,
        "language": "en",
        "consent": None,
        "onboarding_complete": False,
        "current_consent_version": CURRENT_CONSENT_VERSION,
    }
    assert user_id in api.repository.profiles


def test_get_me_is_idempotent(api: Api, user_id: uuid.UUID) -> None:
    api.client.get("/me", headers=api.headers(user_id))
    api.client.get("/me", headers=api.headers(user_id))

    assert len(api.repository.profiles) == 1


def test_patch_me_sets_pseudonym_and_language(api: Api, user_id: uuid.UUID) -> None:
    response = api.client.patch(
        "/me", json={"pseudonym": "Quiet Owl", "language": "de"}, headers=api.headers(user_id)
    )

    assert response.status_code == 200
    assert response.json()["pseudonym"] == "Quiet Owl"
    assert response.json()["language"] == "de"


def test_patch_me_keeps_unset_fields(api: Api, user_id: uuid.UUID) -> None:
    api.client.patch("/me", json={"language": "de"}, headers=api.headers(user_id))

    response = api.client.patch("/me", json={"pseudonym": "Owl"}, headers=api.headers(user_id))

    assert response.json()["language"] == "de"


def test_patch_me_trims_pseudonym(api: Api, user_id: uuid.UUID) -> None:
    response = api.client.patch("/me", json={"pseudonym": "  Owl  "}, headers=api.headers(user_id))

    assert response.json()["pseudonym"] == "Owl"


@pytest.mark.parametrize(
    "pseudonym",
    ["ab", "x" * 25, "Owl<script>", "Owl\nFox", "   ", "@admin", None],
)
def test_patch_me_rejects_invalid_pseudonyms(
    api: Api, user_id: uuid.UUID, pseudonym: str | None
) -> None:
    response = api.client.patch("/me", json={"pseudonym": pseudonym}, headers=api.headers(user_id))

    assert response.status_code == 422


@pytest.mark.parametrize("pseudonym", ["Owl", "Quiet Owl", "Jörg-42", "night_fox", "Ünal"])
def test_patch_me_accepts_valid_pseudonyms(api: Api, user_id: uuid.UUID, pseudonym: str) -> None:
    response = api.client.patch("/me", json={"pseudonym": pseudonym}, headers=api.headers(user_id))

    assert response.status_code == 200


def test_patch_me_rejects_unknown_language(api: Api, user_id: uuid.UUID) -> None:
    response = api.client.patch("/me", json={"language": "fr"}, headers=api.headers(user_id))

    assert response.status_code == 422


def test_post_consent_stores_version_and_time(api: Api, user_id: uuid.UUID) -> None:
    response = api.client.post(
        "/me/consent",
        json={"consent_version": CURRENT_CONSENT_VERSION, "age_confirmed": True},
        headers=api.headers(user_id),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["consent_version"] == CURRENT_CONSENT_VERSION
    assert body["age_confirmed"] is True
    assert body["granted_at"]
    [stored] = api.repository.consents
    assert stored.user_id == user_id


def test_post_consent_requires_age_confirmation(api: Api, user_id: uuid.UUID) -> None:
    assert give_consent(api, user_id, age_confirmed=False) == 422
    assert api.repository.consents == []


def test_post_consent_rejects_outdated_version(api: Api, user_id: uuid.UUID) -> None:
    assert give_consent(api, user_id, consent_version="0") == 422


def test_onboarding_complete_after_consent_and_pseudonym(api: Api, user_id: uuid.UUID) -> None:
    give_consent(api, user_id)
    api.client.patch("/me", json={"pseudonym": "Owl"}, headers=api.headers(user_id))

    body = api.client.get("/me", headers=api.headers(user_id)).json()

    assert body["onboarding_complete"] is True
    assert body["consent"]["consent_version"] == CURRENT_CONSENT_VERSION


def test_require_consent_blocks_without_consent(api: Api, user_id: uuid.UUID) -> None:
    response = api.client.get("/test/game", headers=api.headers(user_id))

    assert response.status_code == 403


def seed_consent(api: Api, user_id: uuid.UUID, *, version: str, age_confirmed: bool) -> None:
    """Store a consent directly, bypassing the endpoint's validation."""
    asyncio.run(
        api.repository.add_consent(user_id, consent_version=version, age_confirmed=age_confirmed)
    )


def test_require_consent_blocks_outdated_consent(api: Api, user_id: uuid.UUID) -> None:
    seed_consent(api, user_id, version="0", age_confirmed=True)

    response = api.client.get("/test/game", headers=api.headers(user_id))

    assert response.status_code == 403


def test_require_consent_blocks_missing_age_confirmation(api: Api, user_id: uuid.UUID) -> None:
    seed_consent(api, user_id, version=CURRENT_CONSENT_VERSION, age_confirmed=False)

    response = api.client.get("/test/game", headers=api.headers(user_id))

    assert response.status_code == 403


def test_require_consent_allows_valid_consent(api: Api, user_id: uuid.UUID) -> None:
    give_consent(api, user_id)

    response = api.client.get("/test/game", headers=api.headers(user_id))

    assert response.status_code == 200
    assert response.json() == {"id": str(user_id)}


def test_require_consent_needs_authentication(api: Api) -> None:
    assert api.client.get("/test/game").status_code == 401
