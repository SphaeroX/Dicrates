import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from tests.auth_helpers import TEST_ISSUER, FakeJwksClient, SigningKey
from tests.profiles.fakes import FakeProfileRepository
from tests.questions.fakes import FakeQuestionRepository
from tests.rooms.fakes import FakeRoomRepository

from dicrates.core.auth import TokenVerifier, get_token_verifier
from dicrates.core.language import Language
from dicrates.core.settings import Settings
from dicrates.main import create_app
from dicrates.profiles.consent import CURRENT_CONSENT_VERSION
from dicrates.profiles.dependencies import get_profile_repository
from dicrates.questions.dependencies import get_question_repository
from dicrates.rooms.dependencies import get_room_repository
from dicrates.rooms.models import NewRoom
from dicrates.rounds.dependencies import get_round_status_reader
from dicrates.rounds.status import RoundStatusView

DEADLINE = datetime(2026, 11, 5, 18, 0, tzinfo=UTC)
NEW_ROOM = NewRoom(
    question_id=uuid.uuid4(), language=Language.EN, round_duration_hours=6, invite_code="K7M2QX"
)


class FakeStatusReader:
    def __init__(self) -> None:
        self.asked: list[tuple[uuid.UUID, uuid.UUID]] = []

    async def status(self, room_id: uuid.UUID, user_id: uuid.UUID) -> RoundStatusView:
        self.asked.append((room_id, user_id))
        return RoundStatusView(
            status="R1_OPEN",
            round_number=1,
            deadline_at=DEADLINE,
            submitted=False,
            submission_count=2,
            member_count=4,
        )


@pytest.fixture
def setup() -> tuple[TestClient, FakeRoomRepository, FakeStatusReader, SigningKey]:
    key = SigningKey(kid="key-1")
    profiles = FakeProfileRepository()
    rooms = FakeRoomRepository()
    reader = FakeStatusReader()
    app = create_app(Settings(_env_file=None))  # pyright: ignore[reportCallIssue]
    app.dependency_overrides[get_token_verifier] = lambda: TokenVerifier(
        jwks_client=FakeJwksClient(key), issuer=TEST_ISSUER
    )
    app.dependency_overrides[get_profile_repository] = lambda: profiles
    app.dependency_overrides[get_question_repository] = FakeQuestionRepository
    app.dependency_overrides[get_room_repository] = lambda: rooms
    app.dependency_overrides[get_round_status_reader] = lambda: reader
    client = TestClient(app)
    client.profiles = profiles  # type: ignore[attr-defined]
    return client, rooms, reader, key


async def consenting(client: TestClient, key: SigningKey) -> tuple[uuid.UUID, dict[str, str]]:
    user_id = uuid.uuid4()
    await client.profiles.add_consent(  # type: ignore[attr-defined]
        user_id, consent_version=CURRENT_CONSENT_VERSION, age_confirmed=True
    )
    return user_id, {"Authorization": f"Bearer {key.token(sub=user_id)}"}


async def test_member_gets_the_round_status(
    setup: tuple[TestClient, FakeRoomRepository, FakeStatusReader, SigningKey],
) -> None:
    client, rooms, reader, key = setup
    user_id, headers = await consenting(client, key)
    room = await rooms.create(
        NewRoom(
            question_id=uuid.uuid4(),
            language=Language.EN,
            round_duration_hours=6,
            invite_code="K7M2QX",
        ),
        creator_id=user_id,
    )

    response = client.get(f"/rooms/{room.id}/status", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "status": "R1_OPEN",
        "round_number": 1,
        "deadline_at": "2026-11-05T18:00:00Z",
        "submitted": False,
        "submission_count": 2,
        "member_count": 4,
    }
    assert reader.asked == [(room.id, user_id)]


async def test_non_members_get_404(
    setup: tuple[TestClient, FakeRoomRepository, FakeStatusReader, SigningKey],
) -> None:
    client, rooms, reader, key = setup
    owner, _ = await consenting(client, key)
    _, stranger = await consenting(client, key)
    room = await rooms.create(
        NewRoom(
            question_id=uuid.uuid4(),
            language=Language.EN,
            round_duration_hours=6,
            invite_code="K7M2QX",
        ),
        creator_id=owner,
    )

    assert client.get(f"/rooms/{room.id}/status", headers=stranger).status_code == 404
    assert reader.asked == []
