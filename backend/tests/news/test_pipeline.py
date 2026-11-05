import json
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from tests.llm.scripted_runner import ScriptedRunner
from tests.news.fakes import FakeNewsRepository
from tests.questions.factories import make_content
from tests.questions.fakes import FakeQuestionRepository

from dicrates.core.language import Language
from dicrates.llm.runner import LlmUnavailableError
from dicrates.news.models import NewsItem
from dicrates.news.pipeline import generate_from_news
from dicrates.questions.models import QuestionOrigin, QuestionStatus

NOW = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)


def item(number: int, outlet: str, language: Language = Language.EN) -> NewsItem:
    return NewsItem(
        url=f"https://news{number}.example.test/story",
        title=f"Invented headline {number} about the car-free square",
        summary=f"Invented summary {number}.",
        outlet=outlet,
        language=language,
        leaning="centre",
        published_at=NOW - timedelta(hours=number),
        expires_at=NOW + timedelta(days=7),
    )


def candidates(*item_lists: list[int]) -> dict[str, Any]:
    return {
        "candidates": [
            {
                "title": f"Car-free square debate {index}",
                "topic_area": "society",
                "item_ids": item_ids,
                "why_controversial": "Residents and shop owners disagree.",
            }
            for index, item_ids in enumerate(item_lists)
        ]
    }


def localized(text: str, source_ids: list[int]) -> dict[str, Any]:
    return {
        "text": text,
        "option_a": None,
        "option_b": None,
        "facts": [{"text": "Invented fact from the reports.", "source_ids": source_ids}],
    }


def draft(source_ids: list[int] | None = None) -> dict[str, Any]:
    ids = source_ids or [1, 2]
    return {
        "format": "scale",
        "topic_area": "society",
        "en": localized("Should Exampleville close its market square to cars?", ids),
        "de": localized("Soll Beispielstadt den Marktplatz für Autos sperren?", ids),
    }


def check(verdict: str, reason: str = "Neutral and concrete.") -> dict[str, Any]:
    return {
        "verdict": verdict,
        "reason": reason,
        "revision_hint": "Avoid the word 'finally'." if verdict == "revise" else None,
    }


@pytest.fixture
async def news() -> FakeNewsRepository:
    repository = FakeNewsRepository()
    await repository.add_new(
        [item(1, "Gazette"), item(2, "Radio"), item(3, "Zeitung", Language.DE)]
    )
    return repository


@pytest.fixture
def questions() -> FakeQuestionRepository:
    return FakeQuestionRepository()


async def test_valid_run_creates_linked_drafts_in_both_languages(
    news: FakeNewsRepository, questions: FakeQuestionRepository
) -> None:
    runner = ScriptedRunner(
        {
            "news_candidates": [candidates([1, 2])],
            "question_draft": [draft()],
            "question_check": [check("ok")],
        }
    )

    report = await generate_from_news(runner=runner, news=news, questions=questions, limit=3)

    stored = list(questions.questions.values())
    assert report.drafts == 1
    assert {question.language for question in stored} == {Language.EN, Language.DE}
    assert len({question.group_id for question in stored}) == 1
    assert stored[0].group_id is not None
    for question in stored:
        assert question.status is QuestionStatus.DRAFT
        assert question.origin is QuestionOrigin.NEWS
        assert question.prompt_version == "question_draft.v1"
        assert [source.outlet for source in question.sources] == ["Gazette", "Radio"]
        assert str(question.sources[0].url) == "https://news1.example.test/story"
        assert question.single_source is False


async def test_sources_come_from_the_items_not_the_model(
    news: FakeNewsRepository, questions: FakeQuestionRepository
) -> None:
    runner = ScriptedRunner(
        {
            "news_candidates": [candidates([2])],
            "question_draft": [draft([1])],
            "question_check": [check("ok")],
        }
    )

    await generate_from_news(runner=runner, news=news, questions=questions, limit=3)

    payload = json.loads(runner.calls_for("question_draft")[0].user_input)
    assert [source["outlet"] for source in payload["sources"]] == ["Radio"]
    stored = next(iter(questions.questions.values()))
    assert stored.single_source is True


async def test_rejected_check_stores_the_reason(
    news: FakeNewsRepository, questions: FakeQuestionRepository
) -> None:
    runner = ScriptedRunner(
        {
            "news_candidates": [candidates([1, 2])],
            "question_draft": [draft()],
            "question_check": [check("reject", "Premise is dehumanising.")],
        }
    )

    report = await generate_from_news(runner=runner, news=news, questions=questions, limit=3)

    assert report.rejected == 1
    assert report.drafts == 0
    for question in questions.questions.values():
        assert question.status is QuestionStatus.REJECTED
        assert question.rejection_reason == "Automatic check: Premise is dehumanising."


async def test_revise_leads_to_exactly_one_revision(
    news: FakeNewsRepository, questions: FakeQuestionRepository
) -> None:
    runner = ScriptedRunner(
        {
            "news_candidates": [candidates([1, 2])],
            "question_draft": [draft(), draft()],
            "question_check": [check("revise", "Loaded word."), check("ok")],
        }
    )

    report = await generate_from_news(runner=runner, news=news, questions=questions, limit=3)

    assert report.drafts == 1
    assert len(runner.calls_for("question_draft")) == 2
    second = json.loads(runner.calls_for("question_draft")[1].user_input)
    assert second["revision_hint"] == "Avoid the word 'finally'."


async def test_second_revise_counts_as_rejection(
    news: FakeNewsRepository, questions: FakeQuestionRepository
) -> None:
    runner = ScriptedRunner(
        {
            "news_candidates": [candidates([1, 2])],
            "question_draft": [draft(), draft(), draft()],
            "question_check": [check("revise"), check("revise", "Still loaded.")],
        }
    )

    report = await generate_from_news(runner=runner, news=news, questions=questions, limit=3)

    assert report.rejected == 1
    assert len(runner.calls_for("question_draft")) == 2
    assert all(q.status is QuestionStatus.REJECTED for q in questions.questions.values())


async def test_invented_source_is_not_stored(
    news: FakeNewsRepository, questions: FakeQuestionRepository
) -> None:
    runner = ScriptedRunner(
        {
            "news_candidates": [candidates([1, 2])],
            "question_draft": [draft([1, 7])],
            "question_check": [check("ok")],
        }
    )

    report = await generate_from_news(runner=runner, news=news, questions=questions, limit=3)

    assert report.discarded == 1
    assert questions.questions == {}
    assert runner.calls_for("question_check") == []


async def test_candidates_with_unknown_items_are_skipped(
    news: FakeNewsRepository, questions: FakeQuestionRepository
) -> None:
    runner = ScriptedRunner(
        {
            "news_candidates": [candidates([42])],
            "question_draft": [draft()],
            "question_check": [check("ok")],
        }
    )

    report = await generate_from_news(runner=runner, news=news, questions=questions, limit=3)

    assert report.discarded == 1
    assert runner.calls_for("question_draft") == []


async def test_existing_questions_are_passed_for_duplicate_protection(
    news: FakeNewsRepository, questions: FakeQuestionRepository
) -> None:
    await questions.create(make_content(text="Should Exampleville build a new tram line?"))
    runner = ScriptedRunner({"news_candidates": [{"candidates": []}]})

    await generate_from_news(runner=runner, news=news, questions=questions, limit=3)

    payload = json.loads(runner.calls_for("news_candidates")[0].user_input)
    assert payload["existing_questions"] == ["Should Exampleville build a new tram line?"]
    assert payload["max_candidates"] == 3
    assert [entry["id"] for entry in payload["items"]] == [1, 2, 3]


async def test_limit_and_llm_failures(
    news: FakeNewsRepository, questions: FakeQuestionRepository
) -> None:
    runner = ScriptedRunner(
        {
            "news_candidates": [candidates([1], [2], [3])],
            "question_draft": [LlmUnavailableError("ModelServerError"), draft([1])],
            "question_check": [check("ok")],
        }
    )

    report = await generate_from_news(runner=runner, news=news, questions=questions, limit=2)

    assert len(runner.calls_for("question_draft")) == 2
    assert report.discarded == 1
    assert report.drafts == 1


async def test_no_news_means_no_llm_call(questions: FakeQuestionRepository) -> None:
    runner = ScriptedRunner({})

    report = await generate_from_news(
        runner=runner, news=FakeNewsRepository(), questions=questions, limit=3
    )

    assert runner.calls == []
    assert report.drafts == 0
