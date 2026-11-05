"""End-to-end email OTP sign-in against the local Supabase stack.

Requests a code from Supabase Auth, reads it from the local Mailpit inbox,
verifies it, and calls `GET /me` with the resulting ES256 access token.

Needs `npx supabase start` with an ES256 signing key (see docs/testing.md) and
`TEST_SUPABASE_ANON_KEY` (from `npx supabase status -o env`); skipped otherwise.
"""

import json
import os
import re
import time
import urllib.request
import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from tests.conftest import integration_database_url

from dicrates.core.settings import Settings
from dicrates.main import create_app

pytestmark = pytest.mark.integration

SUPABASE_URL = os.environ.get("TEST_SUPABASE_URL", "http://127.0.0.1:54321")
MAILPIT_URL = os.environ.get("TEST_MAILPIT_URL", "http://127.0.0.1:54324")
ANON_KEY = os.environ.get("TEST_SUPABASE_ANON_KEY")


def http_json(url: str, *, body: dict[str, Any] | None = None) -> Any:
    headers = {"Content-Type": "application/json"}
    if ANON_KEY and url.startswith(SUPABASE_URL):
        headers["apikey"] = ANON_KEY
    request = urllib.request.Request(  # noqa: S310 - fixed local test URLs
        url,
        data=json.dumps(body).encode() if body is not None else None,
        headers=headers,
        method="POST" if body is not None else "GET",
    )
    with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
        raw = response.read()
    return json.loads(raw) if raw else None


def read_code_from_mailpit(email: str) -> str:
    for _ in range(30):
        found = http_json(f"{MAILPIT_URL}/api/v1/search?query=to:{email}")
        messages: list[dict[str, Any]] = found.get("messages") or []
        if messages:
            message = http_json(f"{MAILPIT_URL}/api/v1/message/{messages[0]['ID']}")
            match = re.search(r"\b(\d{6})\b", message.get("Text") or message.get("HTML") or "")
            if match:
                return match.group(1)
        time.sleep(0.5)
    msg = "no sign-in code arrived in Mailpit"
    raise AssertionError(msg)


@pytest.mark.skipif(
    ANON_KEY is None and os.environ.get("DICRATES_REQUIRE_DB") != "1",
    reason="TEST_SUPABASE_ANON_KEY not set",
)
def test_email_otp_sign_in_reaches_me_endpoint() -> None:
    assert ANON_KEY, "TEST_SUPABASE_ANON_KEY must be set when DICRATES_REQUIRE_DB=1"
    email = f"e2e-{uuid.uuid4().hex[:12]}@example.test"

    http_json(f"{SUPABASE_URL}/auth/v1/otp", body={"email": email, "create_user": True})
    code = read_code_from_mailpit(email)
    session = http_json(
        f"{SUPABASE_URL}/auth/v1/verify", body={"type": "email", "email": email, "token": code}
    )
    access_token = session["access_token"]

    settings = Settings(
        _env_file=None,  # pyright: ignore[reportCallIssue]
        supabase_url=SUPABASE_URL,
        database_url=SecretStr(integration_database_url()),
    )
    with TestClient(create_app(settings)) as client:
        unauthenticated = client.get("/me")
        response = client.get("/me", headers={"Authorization": f"Bearer {access_token}"})

    assert unauthenticated.status_code == 401
    assert response.status_code == 200
    assert response.json()["id"] == session["user"]["id"]
    assert response.json()["onboarding_complete"] is False
