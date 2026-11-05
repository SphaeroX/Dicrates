import json
from typing import Any

import pytest
from tests.llm.scripted_runner import ScriptedRunner
from tests.questions.factories import make_content
from tests.questions.fakes import FakeQuestionRepository

from dicrates.evergreen.pipeline import generate_evergreen
from dicrates.evergreen.topics import EvergreenTopic
from dicrates.questions.models import QuestionOrigin, QuestionStatus


class FakeUrlChecker:
    def __init__(self, unreachable: set[str] | None = None) -> None:
        self.unreachable = unreachable or set()
        self.checked: list[str] = []

    async def is_reachable(self, url: str) -> bool:
        self.checked.append(url)
        return url not in self.unreachable


def topic(topic_id: str = "speed_limit", **overrides: Any) -> EvergreenTopic:
    data: dict[str, Any] = {
        "id": topic_id,
        "title": "General speed limit on motorways",
        "topic_area": "environment",
        "kind": "evergreen",
        "guiding_question": "Should a general motorway speed limit be introduced?",
        "sources": [
            {
                "url": "https://encyclopedia.example.test/speed",
                "title": "Speed limit",
                "outlet": "Encyclopedia",
            },
            {
                "url": "https://agency.example.test/speed",
                "title": "Study",
                "outlet": "Federal Agency",
            },
        ],
    }
    data.update(overrides)
    return EvergreenTopic.model_validate(data)


def localized(text: str) -> dict[str, Any]:
    return {
        "text": text,
        "option_a": None,
        "option_b": None,
        "facts": [{"text": "Invented fact for the test.", "source_ids": [1, 2]}],
    }


DRAFT = {
    "format": "scale",
    "topic_area": "society",  # the topic list decides the area, not the model
    "en": localized("Should Germany introduce a general speed limit on motorways?"),
    "de": localized("Soll Deutschland ein generelles Tempolimit auf Autobahnen einführen?"),
}


def check(verdict: str, reason: str = "Neutral.") -> dict[str, Any]:
    return {"verdict": verdict, "reason": reason, "revision_hint": None}


@pytest.fixture
def questions() -> FakeQuestionRepository:
    return FakeQuestionRepository()


async def test_creates_evergreen_drafts_in_both_languages(
    questions: FakeQuestionRepository,
) -> None:
    runner = ScriptedRunner({"evergreen_question": [DRAFT], "question_check": [check("ok")]})

    report = await generate_evergreen(
        runner=runner, questions=questions, url_checker=FakeUrlChecker(), topics=[topic()], limit=5
    )

    stored = list(questions.questions.values())
    assert report.drafts == 1
    assert len(stored) == 2
    assert len({question.group_id for question in stored}) == 1
    for question in stored:
        assert question.origin is QuestionOrigin.EVERGREEN
        assert question.status is QuestionStatus.DRAFT
        assert question.topic_area == "environment"
        assert question.topic_key == "evergreen:speed_limit"
        assert question.prompt_version == "evergreen_question.v1"
        assert question.review_notes == []
        assert [source.outlet for source in question.sources] == ["Encyclopedia", "Federal Agency"]
    assert runner.calls_for("question_check")[0].prompt.version == "question_check.v2"


async def test_payload_contains_topic_and_numbered_sources(
    questions: FakeQuestionRepository,
) -> None:
    runner = ScriptedRunner({"evergreen_question": [DRAFT], "question_check": [check("ok")]})

    await generate_evergreen(
        runner=runner,
        questions=questions,
        url_checker=FakeUrlChecker(),
        topics=[topic(kind="historical")],
        limit=5,
    )

    payload = json.loads(runner.calls_for("evergreen_question")[0].user_input)
    assert payload["kind"] == "historical"
    assert payload["guiding_question"] == "Should a general motorway speed limit be introduced?"
    assert [source["id"] for source in payload["sources"]] == [1, 2]


async def test_topic_with_an_existing_question_is_skipped(
    questions: FakeQuestionRepository,
) -> None:
    await questions.create(make_content(topic_key="evergreen:speed_limit"))
    runner = ScriptedRunner({"evergreen_question": [DRAFT], "question_check": [check("ok")]})

    report = await generate_evergreen(
        runner=runner, questions=questions, url_checker=FakeUrlChecker(), topics=[topic()], limit=5
    )

    assert report.skipped == 1
    assert runner.calls == []


async def test_unreachable_source_is_marked_not_dropped(
    questions: FakeQuestionRepository,
) -> None:
    runner = ScriptedRunner({"evergreen_question": [DRAFT], "question_check": [check("ok")]})
    checker = FakeUrlChecker(unreachable={"https://agency.example.test/speed"})

    await generate_evergreen(
        runner=runner, questions=questions, url_checker=checker, topics=[topic()], limit=5
    )

    for question in questions.questions.values():
        assert question.status is QuestionStatus.DRAFT
        assert len(question.sources) == 2
        assert question.review_notes == [
            "Source 2 not reachable: https://agency.example.test/speed"
        ]


async def test_dehumanising_premise_is_rejected(questions: FakeQuestionRepository) -> None:
    hostile = {
        **DRAFT,
        "en": localized("Should members of group X lose their right to vote?"),
        "de": localized("Sollen Angehörige der Gruppe X ihr Wahlrecht verlieren?"),
    }
    runner = ScriptedRunner(
        {
            "evergreen_question": [hostile],
            "question_check": [check("reject", "Premise denies a group's basic rights.")],
        }
    )

    report = await generate_evergreen(
        runner=runner, questions=questions, url_checker=FakeUrlChecker(), topics=[topic()], limit=5
    )

    assert report.rejected == 1
    for question in questions.questions.values():
        assert question.status is QuestionStatus.REJECTED
        assert question.rejection_reason == (
            "Automatic check: Premise denies a group's basic rights."
        )


async def test_topic_filter_and_limit(questions: FakeQuestionRepository) -> None:
    runner = ScriptedRunner({"evergreen_question": [DRAFT], "question_check": [check("ok")]})
    topics = [topic("a"), topic("b"), topic("c")]

    only_b = await generate_evergreen(
        runner=runner,
        questions=questions,
        url_checker=FakeUrlChecker(),
        topics=topics,
        limit=5,
        topic_id="b",
    )
    two_more = await generate_evergreen(
        runner=runner, questions=questions, url_checker=FakeUrlChecker(), topics=topics, limit=1
    )

    assert only_b.drafts == 1
    assert two_more.drafts == 1
    keys = {question.topic_key for question in questions.questions.values()}
    assert keys == {"evergreen:b", "evergreen:a"}


async def test_unknown_topic_id_is_an_error(questions: FakeQuestionRepository) -> None:
    with pytest.raises(ValueError, match="unknown topic"):
        await generate_evergreen(
            runner=ScriptedRunner({}),
            questions=questions,
            url_checker=FakeUrlChecker(),
            topics=[topic()],
            limit=1,
            topic_id="nope",
        )
