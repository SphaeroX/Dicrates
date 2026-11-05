import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from dicrates.core.language import Language

MIN_MEMBERS = 3
MAX_MEMBERS = 6
ROUND_DURATIONS_HOURS = (1, 6, 12, 24, 48)
DEFAULT_ROUND_DURATION_HOURS = 24


class RoomStatus(StrEnum):
    """Round state machine (docs/architecture.md). Transitions after start: Task 10."""

    FORMING = "FORMING"
    R1_OPEN = "R1_OPEN"
    R1_CLOSED = "R1_CLOSED"
    R2_OPEN = "R2_OPEN"
    R2_CLOSED = "R2_CLOSED"
    R3_OPEN = "R3_OPEN"
    R3_CLOSED = "R3_CLOSED"
    R4_EVALUATING = "R4_EVALUATING"
    FINISHED = "FINISHED"
    ARCHIVED = "ARCHIVED"
    ABORTED = "ABORTED"


#: Rooms whose invite code is reserved (a code is unique among these).
ACTIVE_STATUSES = frozenset(RoomStatus) - {
    RoomStatus.FINISHED,
    RoomStatus.ARCHIVED,
    RoomStatus.ABORTED,
}


class JoinOutcome(StrEnum):
    ADDED = "added"
    ALREADY_MEMBER = "already_member"
    FULL = "full"
    NOT_FORMING = "not_forming"


class StartOutcome(StrEnum):
    STARTED = "started"
    TOO_FEW = "too_few"
    NOT_FORMING = "not_forming"


class NewRoom(BaseModel):
    model_config = ConfigDict(frozen=True)

    question_id: uuid.UUID
    language: Language
    round_duration_hours: int
    invite_code: str


class Room(NewRoom):
    id: uuid.UUID
    status: RoomStatus
    #: Backend only: never part of an API response.
    creator_id: uuid.UUID
    created_at: datetime
    started_at: datetime | None
    member_count: int
