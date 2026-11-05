import random

import pytest

from dicrates.rooms.invite_codes import (
    INVITE_ALPHABET,
    INVITE_CODE_LENGTH,
    new_invite_code,
    normalize_invite_code,
)


def test_codes_have_the_right_length_and_alphabet() -> None:
    generator = random.Random(1)  # noqa: S311 - deterministic test

    for _ in range(200):
        code = new_invite_code(generator)
        assert len(code) == INVITE_CODE_LENGTH
        assert set(code) <= set(INVITE_ALPHABET)


def test_alphabet_has_no_confusable_characters() -> None:
    assert not set("0O1IL5S") & set(INVITE_ALPHABET)


@pytest.mark.parametrize(
    ("typed", "expected"),
    [("abc234", "ABC234"), (" ABC-234 ", "ABC234"), ("abc 234", "ABC234")],
)
def test_typed_codes_are_normalized(typed: str, expected: str) -> None:
    assert normalize_invite_code(typed) == expected


@pytest.mark.parametrize("typed", ["", "ABC", "ABC2345", "ABC23O", "ABC#34"])
def test_invalid_codes_are_rejected(typed: str) -> None:
    assert normalize_invite_code(typed) is None
