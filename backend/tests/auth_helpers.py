"""Test key pairs, a fake JWKS client and token factory for auth tests."""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from jwt.algorithms import ECAlgorithm

TEST_SUPABASE_URL = "http://supabase.test"
TEST_ISSUER = f"{TEST_SUPABASE_URL}/auth/v1"


@dataclass
class SigningKey:
    kid: str
    private_key: ec.EllipticCurvePrivateKey = field(
        default_factory=lambda: ec.generate_private_key(ec.SECP256R1())
    )

    def public_jwk(self) -> dict[str, Any]:
        jwk: dict[str, Any] = ECAlgorithm.to_jwk(self.private_key.public_key(), as_dict=True)
        return {**jwk, "kid": self.kid, "alg": "ES256", "use": "sig"}

    def token(
        self,
        *,
        sub: uuid.UUID | str | None = None,
        aud: str = "authenticated",
        iss: str = TEST_ISSUER,
        expires_in: int = 3600,
        role: str = "authenticated",
    ) -> str:
        now = int(time.time())
        claims = {
            "sub": str(sub or uuid.uuid4()),
            "aud": aud,
            "iss": iss,
            "iat": now,
            "exp": now + expires_in,
            "role": role,
        }
        return jwt.encode(claims, self.private_key, algorithm="ES256", headers={"kid": self.kid})


class FakeJwksClient(jwt.PyJWKClient):
    """PyJWKClient that serves keys from memory and counts JWKS fetches."""

    def __init__(self, *keys: SigningKey) -> None:
        super().__init__(f"{TEST_SUPABASE_URL}/auth/v1/.well-known/jwks.json", cooldown_duration=0)
        self.keys = list(keys)
        self.fetch_count = 0

    def fetch_data(self) -> Any:
        self.fetch_count += 1
        return {"keys": [key.public_jwk() for key in self.keys]}
