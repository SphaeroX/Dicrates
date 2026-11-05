import uuid
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from tests.auth_helpers import TEST_ISSUER, FakeJwksClient, SigningKey

from dicrates.core.auth import (
    AuthenticatedUser,
    InvalidTokenError,
    TokenVerifier,
    get_current_user,
    get_token_verifier,
)


def make_verifier(jwks: FakeJwksClient) -> TokenVerifier:
    return TokenVerifier(jwks_client=jwks, issuer=TEST_ISSUER)


def test_valid_token_yields_user_id() -> None:
    key = SigningKey(kid="key-1")
    user_id = uuid.uuid4()

    user = make_verifier(FakeJwksClient(key)).verify(key.token(sub=user_id))

    assert user == AuthenticatedUser(id=user_id)


def test_expired_token_is_rejected() -> None:
    key = SigningKey(kid="key-1")

    with pytest.raises(InvalidTokenError):
        make_verifier(FakeJwksClient(key)).verify(key.token(expires_in=-10))


def test_wrong_signature_is_rejected() -> None:
    published = SigningKey(kid="key-1")
    attacker = SigningKey(kid="key-1")  # same kid, different private key

    with pytest.raises(InvalidTokenError):
        make_verifier(FakeJwksClient(published)).verify(attacker.token())


def test_wrong_audience_is_rejected() -> None:
    key = SigningKey(kid="key-1")

    with pytest.raises(InvalidTokenError):
        make_verifier(FakeJwksClient(key)).verify(key.token(aud="something-else"))


def test_wrong_issuer_is_rejected() -> None:
    key = SigningKey(kid="key-1")

    with pytest.raises(InvalidTokenError):
        make_verifier(FakeJwksClient(key)).verify(key.token(iss="http://evil.test/auth/v1"))


def test_symmetric_token_is_rejected() -> None:
    import jwt

    forged = jwt.encode(
        {"sub": str(uuid.uuid4()), "aud": "authenticated", "iss": TEST_ISSUER, "exp": 9999999999},
        "shared-secret-that-is-long-enough-for-hs256",
        algorithm="HS256",
        headers={"kid": "key-1"},
    )

    with pytest.raises(InvalidTokenError):
        make_verifier(FakeJwksClient(SigningKey(kid="key-1"))).verify(forged)


def test_garbage_token_is_rejected() -> None:
    with pytest.raises(InvalidTokenError):
        make_verifier(FakeJwksClient(SigningKey(kid="key-1"))).verify("not-a-jwt")


def test_jwks_is_cached_between_verifications() -> None:
    key = SigningKey(kid="key-1")
    jwks = FakeJwksClient(key)
    verifier = make_verifier(jwks)

    verifier.verify(key.token())
    verifier.verify(key.token())

    assert jwks.fetch_count == 1


def test_jwks_is_reloaded_for_unknown_kid() -> None:
    old_key = SigningKey(kid="old")
    jwks = FakeJwksClient(old_key)
    verifier = make_verifier(jwks)
    verifier.verify(old_key.token())

    rotated_key = SigningKey(kid="new")
    jwks.keys.append(rotated_key)
    user_id = uuid.uuid4()

    assert verifier.verify(rotated_key.token(sub=user_id)) == AuthenticatedUser(id=user_id)
    assert jwks.fetch_count == 2


@pytest.fixture
def key() -> SigningKey:
    return SigningKey(kid="key-1")


@pytest.fixture
def client(key: SigningKey) -> TestClient:
    app = FastAPI()

    @app.get("/whoami")
    def whoami(  # pyright: ignore[reportUnusedFunction]
        user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    ) -> dict[str, str]:
        return {"id": str(user.id)}

    app.dependency_overrides[get_token_verifier] = lambda: make_verifier(FakeJwksClient(key))
    return TestClient(app)


def test_endpoint_accepts_valid_bearer_token(client: TestClient, key: SigningKey) -> None:
    user_id = uuid.uuid4()

    response = client.get("/whoami", headers={"Authorization": f"Bearer {key.token(sub=user_id)}"})

    assert response.status_code == 200
    assert response.json() == {"id": str(user_id)}


def test_endpoint_rejects_missing_header(client: TestClient) -> None:
    response = client.get("/whoami")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "token_kwargs", [{"expires_in": -10}, {"aud": "wrong"}, {"iss": "http://evil.test"}]
)
def test_endpoint_rejects_invalid_tokens(
    client: TestClient, key: SigningKey, token_kwargs: dict[str, object]
) -> None:
    token = key.token(**token_kwargs)  # pyright: ignore[reportArgumentType]

    response = client.get("/whoami", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_endpoint_rejects_foreign_signature(client: TestClient) -> None:
    token = SigningKey(kid="key-1").token()

    response = client.get("/whoami", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
