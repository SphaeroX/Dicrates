"""News → question drafts: topic candidates, then the shared drafting steps.

Nothing is published automatically: results are `draft` (or `rejected` with the
check's reason) and wait for the operator (`dicrates-admin questions approve`).
"""

import json
import logging

from pydantic import BaseModel, Field, ValidationError

from dicrates.llm.prompts import PromptRegistry, default_registry
from dicrates.llm.runner import LlmError, LlmTaskRunner
from dicrates.news.models import NewsItem
from dicrates.news.sources import NewsRepository
from dicrates.questions.drafting import (
    Drafter,
    DraftingReport,
    DraftRequest,
    TopicArea,
    existing_texts,
)
from dicrates.questions.models import QuestionOrigin, Source
from dicrates.questions.repository import QuestionRepository

logger = logging.getLogger(__name__)

RECENT_ITEMS = 80

#: Kept as a name for callers (CLI, job); same counters as the shared report.
PipelineReport = DraftingReport


class Candidate(BaseModel):
    title: str
    topic_area: TopicArea
    item_ids: list[int] = Field(min_length=1, max_length=6)
    why_controversial: str


class CandidateList(BaseModel):
    candidates: list[Candidate] = Field(max_length=10)


def _sources_for(items: list[NewsItem]) -> list[Source]:
    return [
        Source(
            id=number,
            url=item.url,  # pyright: ignore[reportArgumentType]
            title=item.title[:200],
            outlet=item.outlet,
            published_on=item.published_at.date(),
        )
        for number, item in enumerate(items, start=1)
    ]


async def _candidates(
    runner: LlmTaskRunner,
    registry: PromptRegistry,
    items: list[NewsItem],
    existing: list[str],
    limit: int,
) -> list[Candidate]:
    payload = {
        "max_candidates": limit,
        "existing_questions": existing,
        "items": [
            {
                "id": number,
                "title": item.title,
                "summary": item.summary,
                "outlet": item.outlet,
                "language": item.language,
                "published": item.published_at.date().isoformat(),
            }
            for number, item in enumerate(items, start=1)
        ],
    }
    result = await runner.run(
        task="news_candidates",
        prompt=registry.load("news_candidates", version=1).render(),
        output_type=CandidateList,
        user_input=json.dumps(payload, ensure_ascii=False),
    )
    return result.output.candidates[:limit]


async def generate_from_news(
    *,
    runner: LlmTaskRunner,
    news: NewsRepository,
    questions: QuestionRepository,
    limit: int,
    registry: PromptRegistry | None = None,
) -> DraftingReport:
    report = DraftingReport()
    items = await news.recent(limit=RECENT_ITEMS)
    if not items or limit < 1:
        return report
    registry = registry or default_registry()
    try:
        candidates = await _candidates(
            runner, registry, items, await existing_texts(questions), limit
        )
    except LlmError as error:
        logger.warning("news candidates failed: %s", type(error).__name__)
        return report

    drafter = Drafter(
        runner,
        questions,
        registry,
        draft_task="question_draft",
        draft_prompt=registry.load("question_draft", version=1).render(),
    )
    for candidate in candidates:
        selected = [items[i - 1] for i in dict.fromkeys(candidate.item_ids) if 1 <= i <= len(items)]
        if not selected:
            report.discarded += 1
            continue
        sources = _sources_for(selected)
        request = DraftRequest(
            payload={
                "topic": candidate.title,
                "topic_area": candidate.topic_area,
                "why_controversial": candidate.why_controversial,
                "sources": [
                    {
                        "id": source.id,
                        "title": source.title,
                        "outlet": source.outlet,
                        "published": source.published_on.isoformat()
                        if source.published_on
                        else None,
                    }
                    for source in sources
                ],
            },
            sources=sources,
            origin=QuestionOrigin.NEWS,
        )
        try:
            contents, verdict = await drafter.draft_checked(request)
        except (LlmError, ValidationError) as error:
            logger.warning("discarding news candidate: %s", type(error).__name__)
            report.discarded += 1
            continue
        await drafter.store(contents, verdict, report)
    return report
