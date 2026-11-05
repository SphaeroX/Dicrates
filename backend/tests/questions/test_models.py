import pytest
from pydantic import ValidationError
from tests.questions.factories import content_data, make_content, tradeoff_content

from dicrates.questions.models import (
    InvalidTransitionError,
    QuestionContent,
    QuestionFormat,
    QuestionStatus,
    ensure_transition,
)


def test_valid_scale_question() -> None:
    content = make_content()

    assert content.format is QuestionFormat.SCALE
    assert [fact.source_ids for fact in content.facts] == [[1], [1, 2]]


def test_fact_must_reference_an_existing_source() -> None:
    data = content_data(facts=[{"text": "Invented fact.", "source_ids": [3]}])

    with pytest.raises(ValidationError, match="unknown source"):
        QuestionContent.model_validate(data)


def test_fact_needs_at_least_one_source() -> None:
    data = content_data(facts=[{"text": "Invented fact.", "source_ids": []}])

    with pytest.raises(ValidationError):
        QuestionContent.model_validate(data)


def test_source_ids_must_be_unique() -> None:
    data = content_data()
    data["sources"][1]["id"] = 1

    with pytest.raises(ValidationError, match="unique"):
        QuestionContent.model_validate(data)


def test_tradeoff_needs_both_options() -> None:
    with pytest.raises(ValidationError, match="option"):
        QuestionContent.model_validate(content_data(format="tradeoff", option_a="Pool"))


def test_tradeoff_with_options_is_valid() -> None:
    content = tradeoff_content()

    assert content.option_a == "A new swimming pool"


@pytest.mark.parametrize("question_format", ["scale", "proposal"])
def test_other_formats_must_not_have_options(question_format: str) -> None:
    data = content_data(format=question_format, option_a="A", option_b="B")

    with pytest.raises(ValidationError, match="option"):
        QuestionContent.model_validate(data)


def test_source_url_must_be_http() -> None:
    data = content_data()
    data["sources"][0]["url"] = "javascript:alert(1)"

    with pytest.raises(ValidationError):
        QuestionContent.model_validate(data)


def test_needs_facts_and_sources() -> None:
    with pytest.raises(ValidationError):
        QuestionContent.model_validate(content_data(facts=[], sources=[]))


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (QuestionStatus.DRAFT, QuestionStatus.APPROVED),
        (QuestionStatus.DRAFT, QuestionStatus.REJECTED),
        (QuestionStatus.APPROVED, QuestionStatus.RETIRED),
    ],
)
def test_allowed_transitions(current: QuestionStatus, target: QuestionStatus) -> None:
    ensure_transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (QuestionStatus.DRAFT, QuestionStatus.RETIRED),
        (QuestionStatus.APPROVED, QuestionStatus.DRAFT),
        (QuestionStatus.APPROVED, QuestionStatus.REJECTED),
        (QuestionStatus.REJECTED, QuestionStatus.APPROVED),
        (QuestionStatus.RETIRED, QuestionStatus.APPROVED),
        (QuestionStatus.DRAFT, QuestionStatus.DRAFT),
    ],
)
def test_forbidden_transitions(current: QuestionStatus, target: QuestionStatus) -> None:
    with pytest.raises(InvalidTransitionError):
        ensure_transition(current, target)
