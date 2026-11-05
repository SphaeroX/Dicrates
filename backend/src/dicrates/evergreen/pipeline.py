"""Timeless and historical questions from the curated topic list (same check as news)."""

import logging

from pydantic import ValidationError

from dicrates.evergreen.topics import EvergreenTopic
from dicrates.evergreen.url_check import UrlChecker
from dicrates.llm.prompts import PromptRegistry, default_registry
from dicrates.llm.runner import LlmError, LlmTaskRunner
from dicrates.questions.drafting import Drafter, DraftingReport, DraftRequest
from dicrates.questions.models import QuestionOrigin, QuestionStatus, Source
from dicrates.questions.repository import QuestionRepository

logger = logging.getLogger(__name__)


async def _used_topic_keys(questions: QuestionRepository) -> set[str]:
    return {
        question.topic_key
        for question in await questions.list()
        if question.topic_key and question.status is not QuestionStatus.RETIRED
    }


async def generate_evergreen(
    *,
    runner: LlmTaskRunner,
    questions: QuestionRepository,
    url_checker: UrlChecker,
    topics: list[EvergreenTopic],
    limit: int,
    topic_id: str | None = None,
    registry: PromptRegistry | None = None,
) -> DraftingReport:
    if topic_id is not None:
        topics = [topic for topic in topics if topic.id == topic_id]
        if not topics:
            msg = f"unknown topic {topic_id!r}"
            raise ValueError(msg)
    registry = registry or default_registry()
    drafter = Drafter(
        runner,
        questions,
        registry,
        draft_task="evergreen_question",
        draft_prompt=registry.load("evergreen_question", version=1).render(),
    )
    report = DraftingReport()
    used = await _used_topic_keys(questions)
    for topic in topics:
        if report.drafts + report.rejected + report.discarded >= limit:
            break
        if topic.topic_key in used:
            report.skipped += 1
            continue
        sources = [
            Source(id=number, url=source.url, title=source.title, outlet=source.outlet)
            for number, source in enumerate(topic.sources, start=1)
        ]
        notes = [
            f"Source {source.id} not reachable: {source.url}"
            for source in sources
            if not await url_checker.is_reachable(str(source.url))
        ]
        request = DraftRequest(
            payload={
                "topic": topic.title,
                "kind": topic.kind,
                "guiding_question": topic.guiding_question,
                "sources": [
                    {
                        "id": source.id,
                        "title": source.title,
                        "outlet": source.outlet,
                        "url": str(source.url),
                    }
                    for source in sources
                ],
            },
            sources=sources,
            origin=QuestionOrigin.EVERGREEN,
            topic_area=topic.topic_area,
            topic_key=topic.topic_key,
            review_notes=notes,
        )
        try:
            contents, verdict = await drafter.draft_checked(request)
        except (LlmError, ValidationError) as error:
            logger.warning("discarding evergreen topic %s: %s", topic.id, type(error).__name__)
            report.discarded += 1
            continue
        await drafter.store(contents, verdict, report)
        used.add(topic.topic_key)
    return report
