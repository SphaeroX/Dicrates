"""News → question drafts: candidates, bilingual draft, neutrality/safety check, storage.

Nothing is published automatically: results are `draft` (or `rejected` with the
check's reason) and wait for the operator (`dicrates-admin questions approve`).
"""

import json
import logging
import uuid
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from dicrates.core.language import Language
from dicrates.llm.prompts import PromptRegistry, default_registry
from dicrates.llm.runner import LlmError, LlmTaskRunner
from dicrates.news.models import NewsItem
from dicrates.news.sources import NewsRepository
from dicrates.questions import service
from dicrates.questions.models import (
    Fact,
    QuestionContent,
    QuestionFormat,
    QuestionOrigin,
    QuestionStatus,
    Source,
)
from dicrates.questions.repository import QuestionRepository

logger = logging.getLogger(__name__)

TopicArea = Literal[
    "politics",
    "economy",
    "society",
    "environment",
    "technology",
    "sports",
    "culture",
    "education",
    "health",
]
RECENT_ITEMS = 80
EXISTING_QUESTIONS = 100


class Candidate(BaseModel):
    title: str
    topic_area: TopicArea
    item_ids: list[int] = Field(min_length=1, max_length=6)
    why_controversial: str


class CandidateList(BaseModel):
    candidates: list[Candidate] = Field(max_length=10)


class LocalizedDraft(BaseModel):
    text: str
    option_a: str | None = None
    option_b: str | None = None
    facts: list[Fact] = Field(min_length=1, max_length=6)


class DraftOutput(BaseModel):
    format: QuestionFormat
    topic_area: TopicArea
    en: LocalizedDraft
    de: LocalizedDraft


class CheckOutput(BaseModel):
    verdict: Literal["ok", "revise", "reject"]
    reason: str
    revision_hint: str | None = None


@dataclass
class PipelineReport:
    drafts: int = 0
    rejected: int = 0
    discarded: int = 0


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


def _contents(
    output: DraftOutput, sources: list[Source], prompt_version: str
) -> list[QuestionContent]:
    group_id = uuid.uuid4()
    return [
        QuestionContent(
            language=language,
            format=output.format,
            text=localized.text,
            option_a=localized.option_a,
            option_b=localized.option_b,
            facts=localized.facts,
            sources=sources,
            topic_area=output.topic_area,
            origin=QuestionOrigin.NEWS,
            prompt_version=prompt_version,
            group_id=group_id,
        )
        for language, localized in ((Language.EN, output.en), (Language.DE, output.de))
    ]


class _Pipeline:
    def __init__(
        self, runner: LlmTaskRunner, questions: QuestionRepository, registry: PromptRegistry
    ) -> None:
        self._runner = runner
        self._questions = questions
        self._draft_prompt = registry.load("question_draft", version=1).render()
        self._check_prompt = registry.load("question_check", version=1).render()
        self._candidates_prompt = registry.load("news_candidates", version=1).render()

    async def candidates(
        self, items: list[NewsItem], existing: list[str], limit: int
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
        result = await self._runner.run(
            task="news_candidates",
            prompt=self._candidates_prompt,
            output_type=CandidateList,
            user_input=json.dumps(payload, ensure_ascii=False),
        )
        return result.output.candidates[:limit]

    async def draft(
        self, candidate: Candidate, sources: list[Source], hint: str | None
    ) -> list[QuestionContent]:
        payload = {
            "topic": candidate.title,
            "topic_area": candidate.topic_area,
            "why_controversial": candidate.why_controversial,
            "sources": [
                {
                    "id": source.id,
                    "title": source.title,
                    "outlet": source.outlet,
                    "published": source.published_on.isoformat() if source.published_on else None,
                }
                for source in sources
            ],
            "revision_hint": hint,
        }
        result = await self._runner.run(
            task="question_draft",
            prompt=self._draft_prompt,
            output_type=DraftOutput,
            user_input=json.dumps(payload, ensure_ascii=False),
        )
        # Raises ValidationError when a fact cites a source that was not given.
        return _contents(result.output, sources, result.prompt_version)

    async def check(self, contents: list[QuestionContent]) -> CheckOutput:
        payload = [
            content.model_dump(
                mode="json", include={"language", "format", "text", "option_a", "option_b", "facts"}
            )
            for content in contents
        ]
        result = await self._runner.run(
            task="question_check",
            prompt=self._check_prompt,
            output_type=CheckOutput,
            user_input=json.dumps(payload, ensure_ascii=False),
        )
        return result.output

    async def store(self, contents: list[QuestionContent], verdict: CheckOutput) -> QuestionStatus:
        for content in contents:
            question = await self._questions.create(content)
            if verdict.verdict != "ok":
                await service.reject(
                    self._questions, question.id, reason=f"Automatic check: {verdict.reason}"
                )
        return QuestionStatus.DRAFT if verdict.verdict == "ok" else QuestionStatus.REJECTED


async def generate_from_news(
    *,
    runner: LlmTaskRunner,
    news: NewsRepository,
    questions: QuestionRepository,
    limit: int,
    registry: PromptRegistry | None = None,
) -> PipelineReport:
    report = PipelineReport()
    items = await news.recent(limit=RECENT_ITEMS)
    if not items or limit < 1:
        return report
    pipeline = _Pipeline(runner, questions, registry or default_registry())
    existing = [
        question.text
        for question in await questions.list()
        if question.status is not QuestionStatus.RETIRED
    ][:EXISTING_QUESTIONS]

    try:
        candidates = await pipeline.candidates(items, existing, limit)
    except LlmError as error:
        logger.warning("news candidates failed: %s", type(error).__name__)
        return report

    for candidate in candidates:
        selected = [items[i - 1] for i in dict.fromkeys(candidate.item_ids) if 1 <= i <= len(items)]
        if not selected:
            report.discarded += 1
            continue
        sources = _sources_for(selected)
        try:
            contents = await pipeline.draft(candidate, sources, hint=None)
            verdict = await pipeline.check(contents)
            if verdict.verdict == "revise":
                contents = await pipeline.draft(candidate, sources, hint=verdict.revision_hint)
                verdict = await pipeline.check(contents)
                if verdict.verdict == "revise":
                    verdict = CheckOutput(verdict="reject", reason=verdict.reason)
        except (LlmError, ValidationError) as error:
            logger.warning("discarding news candidate: %s", type(error).__name__)
            report.discarded += 1
            continue
        status = await pipeline.store(contents, verdict)
        if status is QuestionStatus.DRAFT:
            report.drafts += 1
        else:
            report.rejected += 1
    return report
