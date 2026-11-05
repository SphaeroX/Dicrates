"""Pure round state machine: which event leads from which status to which (no I/O)."""

from enum import StrEnum

from dicrates.rooms.models import RoomStatus as S


class Event(StrEnum):
    START = "start"  # creator starts the room (3-6 members)
    EXPIRE = "expire"  # room stayed FORMING too long
    CLOSE = "close"  # round deadline passed or everyone submitted
    ADVANCE = "advance"  # after-close steps (e.g. group picture) are done
    FINISH = "finish"  # evaluation is done
    ARCHIVE = "archive"  # finished room leaves the active list
    ABORT = "abort"  # too few submissions or an unrecoverable step


ALLOWED: dict[tuple[S, Event], S] = {
    (S.FORMING, Event.START): S.R1_OPEN,
    (S.FORMING, Event.EXPIRE): S.ABORTED,
    (S.R1_OPEN, Event.CLOSE): S.R1_CLOSED,
    (S.R1_CLOSED, Event.ADVANCE): S.R2_OPEN,
    (S.R2_OPEN, Event.CLOSE): S.R2_CLOSED,
    (S.R2_CLOSED, Event.ADVANCE): S.R3_OPEN,
    (S.R3_OPEN, Event.CLOSE): S.R3_CLOSED,
    (S.R3_CLOSED, Event.ADVANCE): S.R4_EVALUATING,
    (S.R4_EVALUATING, Event.FINISH): S.FINISHED,
    (S.FINISHED, Event.ARCHIVE): S.ARCHIVED,
    **{
        (status, Event.ABORT): S.ABORTED
        for status in (
            S.R1_OPEN,
            S.R1_CLOSED,
            S.R2_OPEN,
            S.R2_CLOSED,
            S.R3_OPEN,
            S.R3_CLOSED,
            S.R4_EVALUATING,
        )
    },
}

_OPEN_ROUNDS = {S.R1_OPEN: 1, S.R2_OPEN: 2, S.R3_OPEN: 3}
_CLOSED_ROUNDS = {S.R1_CLOSED: 1, S.R2_CLOSED: 2, S.R3_CLOSED: 3}


class InvalidTransitionError(ValueError):
    pass


def next_status(current: S, event: Event) -> S:
    try:
        return ALLOWED[(current, event)]
    except KeyError:
        msg = f"event {event} is not allowed in status {current}"
        raise InvalidTransitionError(msg) from None


def open_round_number(status: S) -> int | None:
    """Number of the round that accepts submissions in `status` (1-3), else None."""
    return _OPEN_ROUNDS.get(status)


def closed_round_number(status: S) -> int | None:
    return _CLOSED_ROUNDS.get(status)
