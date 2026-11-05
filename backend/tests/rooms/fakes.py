import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from dicrates.rooms.models import (
    ACTIVE_STATUSES,
    JoinOutcome,
    NewRoom,
    Room,
    RoomStatus,
    StartOutcome,
)
from dicrates.rooms.repository import InviteCodeTakenError


@dataclass
class _Stored:
    room: Room
    members: list[uuid.UUID] = field(default_factory=list[uuid.UUID])


class FakeRoomRepository:
    def __init__(self) -> None:
        self.rooms: dict[uuid.UUID, _Stored] = {}

    def _view(self, stored: _Stored) -> Room:
        return stored.room.model_copy(update={"member_count": len(stored.members)})

    async def create(self, new_room: NewRoom, *, creator_id: uuid.UUID) -> Room:
        if any(
            stored.room.invite_code == new_room.invite_code
            and stored.room.status in ACTIVE_STATUSES
            for stored in self.rooms.values()
        ):
            raise InviteCodeTakenError
        room = Room(
            **new_room.model_dump(),
            id=uuid.uuid4(),
            status=RoomStatus.FORMING,
            creator_id=creator_id,
            created_at=datetime.now(UTC),
            started_at=None,
            member_count=1,
        )
        self.rooms[room.id] = _Stored(room=room, members=[creator_id])
        return room

    async def get(self, room_id: uuid.UUID) -> Room | None:
        stored = self.rooms.get(room_id)
        return None if stored is None else self._view(stored)

    async def find_active_by_code(self, code: str) -> Room | None:
        for stored in self.rooms.values():
            if stored.room.invite_code == code and stored.room.status in ACTIVE_STATUSES:
                return self._view(stored)
        return None

    async def is_member(self, room_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stored = self.rooms.get(room_id)
        return stored is not None and user_id in stored.members

    async def list_for_member(self, user_id: uuid.UUID) -> list[Room]:
        own = [self._view(s) for s in self.rooms.values() if user_id in s.members]
        return sorted(own, key=lambda room: room.created_at, reverse=True)

    async def add_member(
        self, room_id: uuid.UUID, user_id: uuid.UUID, *, max_members: int
    ) -> JoinOutcome:
        stored = self.rooms[room_id]
        if user_id in stored.members:
            return JoinOutcome.ALREADY_MEMBER
        if stored.room.status is not RoomStatus.FORMING:
            return JoinOutcome.NOT_FORMING
        if len(stored.members) >= max_members:
            return JoinOutcome.FULL
        stored.members.append(user_id)
        return JoinOutcome.ADDED

    async def start(
        self, room_id: uuid.UUID, *, min_members: int, max_members: int
    ) -> StartOutcome:
        stored = self.rooms[room_id]
        if stored.room.status is not RoomStatus.FORMING:
            return StartOutcome.NOT_FORMING
        if not min_members <= len(stored.members) <= max_members:
            return StartOutcome.TOO_FEW
        stored.room = stored.room.model_copy(
            update={"status": RoomStatus.R1_OPEN, "started_at": datetime.now(UTC)}
        )
        return StartOutcome.STARTED

    async def remove_member(self, room_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stored = self.rooms[room_id]
        if stored.room.status is not RoomStatus.FORMING or user_id not in stored.members:
            return False
        stored.members.remove(user_id)
        return True

    async def dissolve(self, room_id: uuid.UUID) -> bool:
        stored = self.rooms[room_id]
        if stored.room.status is not RoomStatus.FORMING:
            return False
        stored.room = stored.room.model_copy(update={"status": RoomStatus.ABORTED})
        return True
