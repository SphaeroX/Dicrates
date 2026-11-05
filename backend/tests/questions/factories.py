"""Invented demo questions for tests (no real news content)."""

from typing import Any

from dicrates.questions.models import QuestionContent


def content_data(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "language": "en",
        "format": "scale",
        "text": "Should the town of Exampleville introduce a car-free market square?",
        "option_a": None,
        "option_b": None,
        "facts": [
            {"text": "The square is used by 4,000 cars per day.", "source_ids": [1]},
            {"text": "Two nearby towns tried the same in 2025.", "source_ids": [1, 2]},
        ],
        "sources": [
            {
                "id": 1,
                "url": "https://example.test/traffic-report",
                "title": "Traffic report 2026",
                "outlet": "Exampleville Gazette",
                "published_on": "2026-10-01",
            },
            {
                "id": 2,
                "url": "https://example.test/neighbours",
                "title": "What the neighbours did",
                "outlet": "Regional Radio",
                "published_on": None,
            },
        ],
        "topic_area": "society",
        "origin": "news",
        "prompt_version": "question_draft.v1",
    }
    data.update(overrides)
    return data


def make_content(**overrides: Any) -> QuestionContent:
    return QuestionContent.model_validate(content_data(**overrides))


def tradeoff_content(**overrides: Any) -> QuestionContent:
    return make_content(
        format="tradeoff",
        text="What should have priority in Exampleville's budget?",
        option_a="A new swimming pool",
        option_b="Renovating the schools",
        **overrides,
    )
