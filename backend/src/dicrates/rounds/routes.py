import uuid

from fastapi import APIRouter, HTTPException, status

from dicrates.profiles.dependencies import ConsentedUser
from dicrates.rooms import service as room_service
from dicrates.rooms.dependencies import Rooms
from dicrates.rounds.dependencies import StatusReader
from dicrates.rounds.status import RoundStatusView

router = APIRouter(prefix="/rooms", tags=["rounds"])


@router.get("/{room_id}/status")
async def room_status(
    user: ConsentedUser, rooms: Rooms, reader: StatusReader, room_id: uuid.UUID
) -> RoundStatusView:
    """Phase, deadline, own submission status and submission count of a room."""
    try:
        await room_service.get_room(rooms, user_id=user.id, room_id=room_id)
    except room_service.RoomNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="room_not_found"
        ) from None
    return await reader.status(room_id, user.id)
