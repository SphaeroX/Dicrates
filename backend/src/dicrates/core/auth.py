"""Verification of Supabase access tokens against the project JWKS (ES256).

No shared JWT secret is configured: the public keys come from
`<SUPABASE_URL>/auth/v1/.well-known/jwks.json` and are cached by `PyJWKClient`,
which reloads the key set when a token names an unknown `kid` (key rotation).
"""

import uuid
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from dicrates.core.settings import Settings

SUPABASE_AUDIENCE = "authenticated"
ALLOWED_ALGORITHMS = ["ES256"]


class InvalidTokenError(Exception):
    """The access token is missing, malformed, expired or not ours."""


@dataclass(frozen=True)
class AuthenticatedUser:
    id: uuid.UUID


class TokenVerifier:
    def __init__(
        self,
        *,
        jwks_client: jwt.PyJWKClient,
        issuer: str,
        audience: str = SUPABASE_AUDIENCE,
    ) -> None:
        self._jwks_client = jwks_client
        self._issuer = issuer
        self._audience = audience

    def verify(self, token: str) -> AuthenticatedUser:
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=ALLOWED_ALGORITHMS,
                audience=self._audience,
                issuer=self._issuer,
                options={"require": ["exp", "sub", "aud", "iss"]},
            )
            return AuthenticatedUser(id=uuid.UUID(str(claims["sub"])))
        except (jwt.PyJWTError, ValueError, KeyError) as error:
            # Never include the token or its claims in the message (logs).
            raise InvalidTokenError(error.__class__.__name__) from error


def verifier_for(settings: Settings) -> TokenVerifier:
    if settings.supabase_url is None:
        msg = "SUPABASE_URL must be set to verify access tokens"
        raise RuntimeError(msg)
    base_url = settings.supabase_url.rstrip("/")
    jwks_client = jwt.PyJWKClient(f"{base_url}/auth/v1/.well-known/jwks.json", lifespan=600)
    return TokenVerifier(jwks_client=jwks_client, issuer=f"{base_url}/auth/v1")


def get_token_verifier(request: Request) -> TokenVerifier:
    """FastAPI dependency: the verifier `create_app` built from the settings."""
    verifier: TokenVerifier | None = getattr(request.app.state, "token_verifier", None)
    if verifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="auth_not_configured"
        )
    return verifier


_bearer = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    verifier: Annotated[TokenVerifier, Depends(get_token_verifier)],
) -> AuthenticatedUser:
    # Sync dependency on purpose: FastAPI runs it in a thread pool, so the
    # (rare) blocking JWKS fetch does not block the event loop.
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _UNAUTHORIZED
    try:
        return verifier.verify(credentials.credentials)
    except InvalidTokenError:
        raise _UNAUTHORIZED from None


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
