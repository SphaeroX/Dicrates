import uuid

import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import TEST_ISSUER, FakeJwksClient, SigningKey
from tests.profiles.fakes import FakeProfileRepository
from tests.questions.factories import make_content, tradeoff_content
from tests.questions.fakes import FakeQuestionRepository

from dicrates.core.auth import TokenVerifier, get_token_verifier
from dicrates.core.settings import Settings
from dicrates.main import create_app
from dicrates.profiles.consent import CURRENT_CONSENT_VERSION
from dicrates.profiles.dependencies import get_profile_repository
from dicrates.questions.dependencies import get_question_repository
from dicrates.questions.models import Question
from dicrates.questions.service import approve, retire


class Api:
    def __init__(self) -> None:
        self.key = SigningKey(kid="key-1")
        self.profiles = FakeProfileRepository()
        self.questions = FakeQuestionRepository()
        self.user_id = uuid.uuid4()
        app = create_app(Settings(_env_file=None))  # pyright: ignore[reportCallIssue]
        app.dependency_overrides[get_token_verifier] = lambda: TokenVerifier(
            jwks_client=FakeJwksClient(self.key), issuer=TEST_ISSUER
        )
        app.dependency_overrides[get_profile_repository] = lambda: self.profiles
        app.dependency_overrides[get_question_repository] = lambda: self.questions
        self.client = TestClient(app)
        self.headers = {"Authorization": f"Bearer {self.key.token(sub=self.user_id)}"}

    async def consent(self) -> None:
        await self.profiles.add_consent(
            self.user_id, consent_version=CURRENT_CONSENT_VERSION, age_confirmed=True
        )

    async def approved(self, **overrides: object) -> Question:
        question = await self.questions.create(make_content(**overrides))
        return await approve(self.questions, question.id)


@pytest.fixture
def api() -> Api:
    return Api()


async def test_lists_only_approved_questions_in_the_language(api: Api) -> None:
    await api.consent()
    english = await api.approved()
    await api.approved(language="de", text="Soll Beispielstadt den Marktplatz autofrei machen?")
    await api.questions.create(make_content())  # draft
    retired = await api.approved()
    await retire(api.questions, retired.id)

    response = api.client.get("/questions", params={"language": "en"}, headers=api.headers)

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [str(english.id)]


async def test_filters_by_topic_area(api: Api) -> None:
    await api.consent()
    society = await api.approved()
    await api.approved(topic_area="environment")

    response = api.client.get(
        "/questions", params={"language": "en", "topic_area": "society"}, headers=api.headers
    )

    assert [item["id"] for item in response.json()] == [str(society.id)]


async def test_question_payload_has_no_internal_fields(api: Api) -> None:
    await api.consent()
    question = await api.questions.create(tradeoff_content())
    await approve(api.questions, question.id)

    body = api.client.get(f"/questions/{question.id}", headers=api.headers).json()

    assert body["option_a"] == "A new swimming pool"
    assert body["facts"][0]["source_ids"] == [1]
    assert body["sources"][0]["url"] == "https://example.test/traffic-report"
    assert "status" not in body
    assert "rejection_reason" not in body
    assert "prompt_version" not in body


async def test_unapproved_question_is_not_found(api: Api) -> None:
    await api.consent()
    draft = await api.questions.create(make_content())

    response = api.client.get(f"/questions/{draft.id}", headers=api.headers)

    assert response.status_code == 404


async def test_questions_require_consent(api: Api) -> None:
    await api.approved()

    assert (
        api.client.get("/questions", params={"language": "en"}, headers=api.headers).status_code
        == 403
    )


def test_questions_require_authentication(api: Api) -> None:
    assert api.client.get("/questions", params={"language": "en"}).status_code == 401
