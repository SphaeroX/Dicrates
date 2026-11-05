import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict

from dicrates.core.language import Language
from dicrates.profiles.dependencies import ConsentedUser
from dicrates.questions.dependencies import Questions
from dicrates.questions.routes import QuestionOut
from dicrates.rooms import service
from dicrates.rooms.dependencies import Rooms
from dicrates.rooms.models import (
    DEFAULT_ROUND_DURATION_HOURS,
    MAX_MEMBERS,
    MIN_MEMBERS,
    Room,
    RoomStatus,
)

router = APIRouter(prefix="/rooms", tags=["rooms"])

_STATUS_CODES: dict[type[service.RoomError], int] = {
    service.QuestionUnavailableError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    service.RoomNotFoundError: status.HTTP_404_NOT_FOUND,
    service.RoomFullError: status.HTTP_409_CONFLICT,
    service.RoomAlreadyStartedError: status.HTTP_409_CONFLICT,
    service.NotCreatorError: status.HTTP_403_FORBIDDEN,
    service.TooFewMembersError: status.HTTP_409_CONFLICT,
}


def _http_error(error: service.RoomError) -> HTTPException:
    return HTTPException(status_code=_STATUS_CODES[type(error)], detail=error.code)


class CreateRoomIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: uuid.UUID
    round_duration_hours: int = DEFAULT_ROUND_DURATION_HOURS


class JoinRoomIn(BaseModel):
    code: str


class RoomOut(BaseModel):
    """A room as its members see it: counts only, never who the other members are."""

    id: uuid.UUID
    status: RoomStatus
    language: Language
    question: QuestionOut | None
    round_duration_hours: int
    invite_code: str
    member_count: int
    min_members: int
    max_members: int
    is_creator: bool
    created_at: datetime
    started_at: datetime | None


async def _out(room: Room, questions: Questions, user_id: uuid.UUID) -> RoomOut:
    question = await questions.get(room.question_id)
    return RoomOut(
        id=room.id,
        status=room.status,
        language=room.language,
        question=QuestionOut.of(question) if question is not None else None,
        round_duration_hours=room.round_duration_hours,
        invite_code=room.invite_code,
        member_count=room.member_count,
        min_members=MIN_MEMBERS,
        max_members=MAX_MEMBERS,
        is_creator=room.creator_id == user_id,
        created_at=room.created_at,
        started_at=room.started_at,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_room(
    user: ConsentedUser, rooms: Rooms, questions: Questions, body: CreateRoomIn
) -> RoomOut:
    try:
        room = await service.create_room(
            rooms,
            questions,
            creator_id=user.id,
            question_id=body.question_id,
            round_duration_hours=body.round_duration_hours,
        )
    except service.RoomError as error:
        raise _http_error(error) from None
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="invalid_round_duration"
        ) from error
    return await _out(room, questions, user.id)


@router.get("")
async def list_rooms(user: ConsentedUser, rooms: Rooms, questions: Questions) -> list[RoomOut]:
    """The caller's rooms, newest first."""
    return [await _out(room, questions, user.id) for room in await rooms.list_for_member(user.id)]


@router.post("/join")
async def join_room(
    user: ConsentedUser, rooms: Rooms, questions: Questions, body: JoinRoomIn
) -> RoomOut:
    try:
        room = await service.join_room(rooms, user_id=user.id, code=body.code)
    except service.RoomError as error:
        raise _http_error(error) from None
    return await _out(room, questions, user.id)


@router.get("/{room_id}")
async def get_room(
    user: ConsentedUser, rooms: Rooms, questions: Questions, room_id: uuid.UUID
) -> RoomOut:
    try:
        room = await service.get_room(rooms, user_id=user.id, room_id=room_id)
    except service.RoomError as error:
        raise _http_error(error) from None
    return await _out(room, questions, user.id)


@router.post("/{room_id}/start")
async def start_room(
    user: ConsentedUser, rooms: Rooms, questions: Questions, room_id: uuid.UUID
) -> RoomOut:
    try:
        room = await service.start_room(rooms, user_id=user.id, room_id=room_id)
    except service.RoomError as error:
        raise _http_error(error) from None
    return await _out(room, questions, user.id)


@router.post("/{room_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_room(user: ConsentedUser, rooms: Rooms, room_id: uuid.UUID) -> Response:
    """Leave a forming room; for the creator this dissolves it."""
    try:
        await service.leave_room(rooms, user_id=user.id, room_id=room_id)
    except service.RoomError as error:
        raise _http_error(error) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)
