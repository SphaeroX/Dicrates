import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import TEST_ISSUER, FakeJwksClient, SigningKey
from tests.profiles.fakes import FakeProfileRepository
from tests.questions.factories import make_content
from tests.questions.fakes import FakeQuestionRepository
from tests.rooms.fakes import FakeRoomRepository

from dicrates.core.auth import TokenVerifier, get_token_verifier
from dicrates.core.settings import Settings
from dicrates.main import create_app
from dicrates.profiles.consent import CURRENT_CONSENT_VERSION
from dicrates.profiles.dependencies import get_profile_repository
from dicrates.questions import service as question_service
from dicrates.questions.dependencies import get_question_repository
from dicrates.rooms.dependencies import get_room_repository


class Api:
    def __init__(self) -> None:
        self.key = SigningKey(kid="key-1")
        self.profiles = FakeProfileRepository()
        self.questions = FakeQuestionRepository()
        self.rooms = FakeRoomRepository()
        app = create_app(Settings(_env_file=None))  # pyright: ignore[reportCallIssue]
        app.dependency_overrides[get_token_verifier] = lambda: TokenVerifier(
            jwks_client=FakeJwksClient(self.key), issuer=TEST_ISSUER
        )
        app.dependency_overrides[get_profile_repository] = lambda: self.profiles
        app.dependency_overrides[get_question_repository] = lambda: self.questions
        app.dependency_overrides[get_room_repository] = lambda: self.rooms
        self.client = TestClient(app)

    async def user(self) -> dict[str, str]:
        user_id = uuid.uuid4()
        await self.profiles.add_consent(
            user_id, consent_version=CURRENT_CONSENT_VERSION, age_confirmed=True
        )
        await self.profiles.update(user_id, self.profiles_update("Owl"))
        return {"Authorization": f"Bearer {self.key.token(sub=user_id)}", "X-User": str(user_id)}

    @staticmethod
    def profiles_update(pseudonym: str) -> Any:
        from dicrates.profiles.models import ProfileUpdate

        return ProfileUpdate(pseudonym=pseudonym)

    async def question_id(self) -> str:
        question = await self.questions.create(make_content())
        await question_service.approve(self.questions, question.id)
        return str(question.id)

    def create(self, headers: dict[str, str], question_id: str, **body: Any) -> Any:
        return self.client.post(
            "/rooms",
            json={"question_id": question_id, "round_duration_hours": 24, **body},
            headers=headers,
        )


@pytest.fixture
def api() -> Api:
    return Api()


async def test_full_lobby_flow(api: Api) -> None:
    creator, second, third = await api.user(), await api.user(), await api.user()

    created = api.create(creator, await api.question_id())
    assert created.status_code == 201
    room = created.json()
    code = room["invite_code"]

    assert (
        api.client.post("/rooms/join", json={"code": code.lower()}, headers=second).status_code
        == 200
    )
    assert api.client.post("/rooms/join", json={"code": code}, headers=third).status_code == 200
    started = api.client.post(f"/rooms/{room['id']}/start", headers=creator)

    assert started.status_code == 200
    assert started.json()["status"] == "R1_OPEN"
    assert started.json()["member_count"] == 3


async def test_room_view_shape_has_no_member_identities(api: Api) -> None:
    creator, friend = await api.user(), await api.user()
    room = api.create(creator, await api.question_id()).json()
    api.client.post("/rooms/join", json={"code": room["invite_code"]}, headers=friend)

    for headers, is_creator in ((creator, True), (friend, False)):
        body = api.client.get(f"/rooms/{room['id']}", headers=headers).json()
        assert body["is_creator"] is is_creator
        assert body["member_count"] == 2
        assert body["min_members"] == 3
        assert body["max_members"] == 6
        assert body["question"]["text"].startswith("Should the town")
        text = str(body)
        assert creator["X-User"] not in text
        assert friend["X-User"] not in text
        assert "creator_id" not in body
        assert "Owl" not in text


async def test_list_shows_only_own_rooms(api: Api) -> None:
    alice, bob = await api.user(), await api.user()
    mine = api.create(alice, await api.question_id()).json()
    api.create(bob, await api.question_id())

    listed = api.client.get("/rooms", headers=alice).json()

    assert [room["id"] for room in listed] == [mine["id"]]


async def test_error_codes(api: Api) -> None:
    creator, friend = await api.user(), await api.user()
    room = api.create(creator, await api.question_id()).json()
    api.client.post("/rooms/join", json={"code": room["invite_code"]}, headers=friend)

    unknown = api.client.post("/rooms/join", json={"code": "ZZZ999"}, headers=friend)
    not_creator = api.client.post(f"/rooms/{room['id']}/start", headers=friend)
    too_few = api.client.post(f"/rooms/{room['id']}/start", headers=creator)
    stranger = api.client.get(f"/rooms/{room['id']}", headers=await api.user())
    bad_duration = api.create(creator, await api.question_id(), round_duration_hours=5)
    draft = await api.questions.create(make_content())
    unavailable = api.create(creator, str(draft.id))

    assert unknown.status_code == 404
    assert not_creator.status_code == 403
    assert too_few.status_code == 409
    assert too_few.json()["detail"] == "too_few_members"
    assert stranger.status_code == 404
    assert bad_duration.status_code == 422
    assert unavailable.status_code == 422


async def test_full_and_started_rooms_answer_409(api: Api) -> None:
    creator = await api.user()
    room = api.create(creator, await api.question_id()).json()
    for _ in range(5):
        api.client.post("/rooms/join", json={"code": room["invite_code"]}, headers=await api.user())

    full = api.client.post(
        "/rooms/join", json={"code": room["invite_code"]}, headers=await api.user()
    )
    api.client.post(f"/rooms/{room['id']}/start", headers=creator)
    started = api.client.post(
        "/rooms/join", json={"code": room["invite_code"]}, headers=await api.user()
    )

    assert full.status_code == 409
    assert full.json()["detail"] == "room_full"
    assert started.status_code == 409
    assert started.json()["detail"] == "room_already_started"


async def test_leave(api: Api) -> None:
    creator, friend = await api.user(), await api.user()
    room = api.create(creator, await api.question_id()).json()
    api.client.post("/rooms/join", json={"code": room["invite_code"]}, headers=friend)

    response = api.client.post(f"/rooms/{room['id']}/leave", headers=friend)

    assert response.status_code == 204
    assert api.client.get("/rooms", headers=friend).json() == []


async def test_rooms_require_consent(api: Api) -> None:
    headers = {"Authorization": f"Bearer {api.key.token(sub=uuid.uuid4())}"}

    assert api.client.get("/rooms", headers=headers).status_code == 403
