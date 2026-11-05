import itertools

import pytest

from dicrates.rooms.models import RoomStatus as S
from dicrates.rounds.state_machine import (
    ALLOWED,
    Event,
    InvalidTransitionError,
    next_status,
    open_round_number,
)

EXPECTED = {
    (S.FORMING, Event.START): S.R1_OPEN,
    (S.FORMING, Event.EXPIRE): S.ABORTED,
    (S.R1_OPEN, Event.CLOSE): S.R1_CLOSED,
    (S.R1_OPEN, Event.ABORT): S.ABORTED,
    (S.R1_CLOSED, Event.ADVANCE): S.R2_OPEN,
    (S.R1_CLOSED, Event.ABORT): S.ABORTED,
    (S.R2_OPEN, Event.CLOSE): S.R2_CLOSED,
    (S.R2_OPEN, Event.ABORT): S.ABORTED,
    (S.R2_CLOSED, Event.ADVANCE): S.R3_OPEN,
    (S.R2_CLOSED, Event.ABORT): S.ABORTED,
    (S.R3_OPEN, Event.CLOSE): S.R3_CLOSED,
    (S.R3_OPEN, Event.ABORT): S.ABORTED,
    (S.R3_CLOSED, Event.ADVANCE): S.R4_EVALUATING,
    (S.R3_CLOSED, Event.ABORT): S.ABORTED,
    (S.R4_EVALUATING, Event.FINISH): S.FINISHED,
    (S.R4_EVALUATING, Event.ABORT): S.ABORTED,
    (S.FINISHED, Event.ARCHIVE): S.ARCHIVED,
}


def test_table_is_exactly_the_expected_one() -> None:
    assert ALLOWED == EXPECTED


@pytest.mark.parametrize(("current", "event"), list(EXPECTED))
def test_allowed_transitions(current: S, event: Event) -> None:
    assert next_status(current, event) is EXPECTED[(current, event)]


@pytest.mark.parametrize(
    ("current", "event"),
    [pair for pair in itertools.product(S, Event) if pair not in EXPECTED],
)
def test_every_other_transition_is_forbidden(current: S, event: Event) -> None:
    with pytest.raises(InvalidTransitionError):
        next_status(current, event)


def test_final_states_have_no_way_out() -> None:
    for final in (S.ARCHIVED, S.ABORTED):
        assert not [event for (state, event) in ALLOWED if state is final]


@pytest.mark.parametrize(
    ("status", "number"),
    [(S.R1_OPEN, 1), (S.R2_OPEN, 2), (S.R3_OPEN, 3), (S.FORMING, None), (S.R1_CLOSED, None)],
)
def test_open_round_number(status: S, number: int | None) -> None:
    assert open_round_number(status) == number
