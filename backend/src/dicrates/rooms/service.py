"""Friend rooms: create, join by code, start, leave. Members stay anonymous to each other."""

import uuid
from collections.abc import Callable

from dicrates.questions.models import QuestionStatus
from dicrates.questions.repository import QuestionRepository
from dicrates.rooms.invite_codes import new_invite_code, normalize_invite_code
from dicrates.rooms.models import (
    MAX_MEMBERS,
    MIN_MEMBERS,
    ROUND_DURATIONS_HOURS,
    JoinOutcome,
    NewRoom,
    Room,
    RoomStatus,
    StartOutcome,
)
from dicrates.rooms.repository import InviteCodeTakenError, RoomRepository

__all__ = ["Room"]

_CODE_ATTEMPTS = 10


class RoomError(Exception):
    """Base class; `code` is the stable API error detail."""

    code = "room_error"


class QuestionUnavailableError(RoomError):
    code = "question_unavailable"


class RoomNotFoundError(RoomError):
    code = "room_not_found"


class RoomFullError(RoomError):
    code = "room_full"


class RoomAlreadyStartedError(RoomError):
    code = "room_already_started"


class NotCreatorError(RoomError):
    code = "not_creator"


class TooFewMembersError(RoomError):
    code = "too_few_members"


async def create_room(
    rooms: RoomRepository,
    questions: QuestionRepository,
    *,
    creator_id: uuid.UUID,
    question_id: uuid.UUID,
    round_duration_hours: int,
    new_code: Callable[[], str] = new_invite_code,
) -> Room:
    if round_duration_hours not in ROUND_DURATIONS_HOURS:
        msg = f"round duration must be one of {ROUND_DURATIONS_HOURS} hours"
        raise ValueError(msg)
    question = await questions.get(question_id)
    if question is None or question.status is not QuestionStatus.APPROVED:
        raise QuestionUnavailableError
    for _ in range(_CODE_ATTEMPTS):
        try:
            return await rooms.create(
                NewRoom(
                    question_id=question.id,
                    language=question.language,
                    round_duration_hours=round_duration_hours,
                    invite_code=new_code(),
                ),
                creator_id=creator_id,
            )
        except InviteCodeTakenError:
            continue
    msg = "could not find a free invite code"
    raise RuntimeError(msg)


async def get_room(rooms: RoomRepository, *, user_id: uuid.UUID, room_id: uuid.UUID) -> Room:
    """The room, if the user is an active member (otherwise it does not exist for them)."""
    room = await rooms.get(room_id)
    if room is None or not await rooms.is_member(room_id, user_id):
        raise RoomNotFoundError
    return room


async def join_room(rooms: RoomRepository, *, user_id: uuid.UUID, code: str) -> Room:
    normalized = normalize_invite_code(code)
    room = await rooms.find_active_by_code(normalized) if normalized else None
    if room is None:
        raise RoomNotFoundError
    match await rooms.add_member(room.id, user_id, max_members=MAX_MEMBERS):
        case JoinOutcome.ADDED | JoinOutcome.ALREADY_MEMBER:
            return await get_room(rooms, user_id=user_id, room_id=room.id)
        case JoinOutcome.FULL:
            raise RoomFullError
        case JoinOutcome.NOT_FORMING:
            raise RoomAlreadyStartedError


async def start_room(rooms: RoomRepository, *, user_id: uuid.UUID, room_id: uuid.UUID) -> Room:
    room = await get_room(rooms, user_id=user_id, room_id=room_id)
    if room.creator_id != user_id:
        raise NotCreatorError
    match await rooms.start(room_id, min_members=MIN_MEMBERS, max_members=MAX_MEMBERS):
        case StartOutcome.STARTED:
            return await get_room(rooms, user_id=user_id, room_id=room_id)
        case StartOutcome.TOO_FEW:
            raise TooFewMembersError
        case StartOutcome.NOT_FORMING:
            raise RoomAlreadyStartedError


async def leave_room(rooms: RoomRepository, *, user_id: uuid.UUID, room_id: uuid.UUID) -> None:
    """Members leave while the room forms; the creator leaving dissolves the room."""
    room = await get_room(rooms, user_id=user_id, room_id=room_id)
    if room.status is not RoomStatus.FORMING:
        raise RoomAlreadyStartedError
    if room.creator_id == user_id:
        await rooms.dissolve(room_id)
    else:
        await rooms.remove_member(room_id, user_id)
