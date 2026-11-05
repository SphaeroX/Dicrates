import itertools
import uuid

import pytest
from tests.questions.factories import make_content
from tests.questions.fakes import FakeQuestionRepository
from tests.rooms.fakes import FakeRoomRepository

from dicrates.questions import service as question_service
from dicrates.rooms import service
from dicrates.rooms.models import RoomStatus


class World:
    def __init__(self) -> None:
        self.rooms = FakeRoomRepository()
        self.questions = FakeQuestionRepository()
        self.codes = itertools.cycle(["ABC234", "ABC234", "XYZ789", "KMN234", "PQR678"])

    def next_code(self) -> str:
        return next(self.codes)

    async def approved_question(self, **overrides: object) -> uuid.UUID:
        question = await self.questions.create(make_content(**overrides))
        await question_service.approve(self.questions, question.id)
        return question.id

    async def create(self, creator: uuid.UUID, **overrides: object) -> service.Room:
        return await service.create_room(
            self.rooms,
            self.questions,
            creator_id=creator,
            question_id=await self.approved_question(**overrides),
            round_duration_hours=24,
            new_code=self.next_code,
        )


@pytest.fixture
def world() -> World:
    return World()


def users(count: int) -> list[uuid.UUID]:
    return [uuid.uuid4() for _ in range(count)]


async def test_create_room_with_an_approved_question(world: World) -> None:
    [creator] = users(1)

    room = await world.create(creator, language="de", text="Soll Beispielstadt autofrei werden?")

    assert room.status is RoomStatus.FORMING
    assert room.language == "de"
    assert room.member_count == 1
    assert room.round_duration_hours == 24
    assert await world.rooms.is_member(room.id, creator)


async def test_create_needs_an_approved_question(world: World) -> None:
    draft = await world.questions.create(make_content())

    with pytest.raises(service.QuestionUnavailableError):
        await service.create_room(
            world.rooms,
            world.questions,
            creator_id=uuid.uuid4(),
            question_id=draft.id,
            round_duration_hours=24,
            new_code=world.next_code,
        )


async def test_create_rejects_unknown_durations(world: World) -> None:
    with pytest.raises(ValueError, match="duration"):
        await service.create_room(
            world.rooms,
            world.questions,
            creator_id=uuid.uuid4(),
            question_id=await world.approved_question(),
            round_duration_hours=5,
            new_code=world.next_code,
        )


async def test_invite_code_collisions_are_retried(world: World) -> None:
    first = await world.create(uuid.uuid4())
    second = await world.create(uuid.uuid4())

    assert first.invite_code == "ABC234"
    assert second.invite_code == "XYZ789"


async def test_join_with_code(world: World) -> None:
    creator, friend = users(2)
    room = await world.create(creator)

    joined = await service.join_room(world.rooms, user_id=friend, code="abc-234")

    assert joined.id == room.id
    assert joined.member_count == 2


async def test_join_twice_is_idempotent(world: World) -> None:
    creator, friend = users(2)
    await world.create(creator)

    await service.join_room(world.rooms, user_id=friend, code="ABC234")
    again = await service.join_room(world.rooms, user_id=friend, code="ABC234")

    assert again.member_count == 2


@pytest.mark.parametrize("code", ["ZZZ999", "not a code"])
async def test_join_unknown_code(world: World, code: str) -> None:
    with pytest.raises(service.RoomNotFoundError):
        await service.join_room(world.rooms, user_id=uuid.uuid4(), code=code)


async def test_join_full_room(world: World) -> None:
    creator, *others = users(7)
    await world.create(creator)
    for user in others[:5]:
        await service.join_room(world.rooms, user_id=user, code="ABC234")

    with pytest.raises(service.RoomFullError):
        await service.join_room(world.rooms, user_id=others[5], code="ABC234")


async def test_join_started_room(world: World) -> None:
    creator, *others = users(4)
    room = await world.create(creator)
    for user in others[:2]:
        await service.join_room(world.rooms, user_id=user, code="ABC234")
    await service.start_room(world.rooms, user_id=creator, room_id=room.id)

    with pytest.raises(service.RoomAlreadyStartedError):
        await service.join_room(world.rooms, user_id=others[2], code="ABC234")


async def test_start_rules(world: World) -> None:
    creator, friend, third = users(3)
    room = await world.create(creator)
    await service.join_room(world.rooms, user_id=friend, code="ABC234")

    with pytest.raises(service.NotCreatorError):
        await service.start_room(world.rooms, user_id=friend, room_id=room.id)
    with pytest.raises(service.TooFewMembersError):
        await service.start_room(world.rooms, user_id=creator, room_id=room.id)

    await service.join_room(world.rooms, user_id=third, code="ABC234")
    started = await service.start_room(world.rooms, user_id=creator, room_id=room.id)

    assert started.status is RoomStatus.R1_OPEN
    assert started.started_at is not None
    with pytest.raises(service.RoomAlreadyStartedError):
        await service.start_room(world.rooms, user_id=creator, room_id=room.id)


async def test_non_members_cannot_see_a_room(world: World) -> None:
    room = await world.create(uuid.uuid4())

    with pytest.raises(service.RoomNotFoundError):
        await service.get_room(world.rooms, user_id=uuid.uuid4(), room_id=room.id)


async def test_leave_and_dissolve(world: World) -> None:
    creator, friend = users(2)
    room = await world.create(creator)
    await service.join_room(world.rooms, user_id=friend, code="ABC234")

    await service.leave_room(world.rooms, user_id=friend, room_id=room.id)
    assert (await world.rooms.get(room.id)).member_count == 1  # type: ignore[union-attr]

    await service.leave_room(world.rooms, user_id=creator, room_id=room.id)  # creator dissolves
    assert (await world.rooms.get(room.id)).status is RoomStatus.ABORTED  # type: ignore[union-attr]
    with pytest.raises(service.RoomNotFoundError):
        await service.join_room(world.rooms, user_id=friend, code="ABC234")


async def test_cannot_leave_after_start(world: World) -> None:
    creator, *others = users(3)
    room = await world.create(creator)
    for user in others:
        await service.join_room(world.rooms, user_id=user, code="ABC234")
    await service.start_room(world.rooms, user_id=creator, room_id=room.id)

    with pytest.raises(service.RoomAlreadyStartedError):
        await service.leave_room(world.rooms, user_id=others[0], room_id=room.id)
