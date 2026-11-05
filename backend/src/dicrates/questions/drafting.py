"""Shared LLM drafting for generated questions: bilingual draft, check, one revision, storage.

Used by the news pipeline (`dicrates.news.pipeline`) and the evergreen pipeline
(`dicrates.evergreen.pipeline`). Sources are always built by the caller from
trusted data; the model only cites them by number.
"""

import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel, Field

from dicrates.core.language import Language
from dicrates.llm.prompts import PromptRegistry, RenderedPrompt
from dicrates.llm.runner import LlmTaskRunner
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

CHECK_PROMPT = ("question_check", 2)


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
class DraftingReport:
    drafts: int = 0
    rejected: int = 0
    discarded: int = 0
    skipped: int = 0


@dataclass(frozen=True)
class DraftRequest:
    """One question to draft: task-specific payload plus the trusted sources."""

    payload: dict[str, Any]
    sources: list[Source]
    origin: QuestionOrigin
    topic_area: str | None = None  # overrides the model's choice when set
    topic_key: str | None = None
    review_notes: list[str] = field(default_factory=list[str])


class Drafter:
    def __init__(
        self,
        runner: LlmTaskRunner,
        questions: QuestionRepository,
        registry: PromptRegistry,
        *,
        draft_task: str,
        draft_prompt: RenderedPrompt,
    ) -> None:
        self._runner = runner
        self._questions = questions
        self._draft_task = draft_task
        self._draft_prompt = draft_prompt
        name, version = CHECK_PROMPT
        self._check_prompt = registry.load(name, version=version).render()

    async def _draft(self, request: DraftRequest, hint: str | None) -> list[QuestionContent]:
        result = await self._runner.run(
            task=self._draft_task,
            prompt=self._draft_prompt,
            output_type=DraftOutput,
            user_input=json.dumps({**request.payload, "revision_hint": hint}, ensure_ascii=False),
        )
        output = result.output
        group_id = uuid.uuid4()
        # Raises ValidationError when a fact cites a source that was not given.
        return [
            QuestionContent(
                language=language,
                format=output.format,
                text=localized.text,
                option_a=localized.option_a,
                option_b=localized.option_b,
                facts=localized.facts,
                sources=request.sources,
                topic_area=request.topic_area or output.topic_area,
                origin=request.origin,
                prompt_version=result.prompt_version,
                group_id=group_id,
                topic_key=request.topic_key,
                review_notes=request.review_notes,
            )
            for language, localized in ((Language.EN, output.en), (Language.DE, output.de))
        ]

    async def _check(self, contents: list[QuestionContent]) -> CheckOutput:
        fields = {"language", "format", "text", "option_a", "option_b", "facts"}
        payload = [content.model_dump(mode="json", include=fields) for content in contents]
        result = await self._runner.run(
            task="question_check",
            prompt=self._check_prompt,
            output_type=CheckOutput,
            user_input=json.dumps(payload, ensure_ascii=False),
        )
        return result.output

    async def draft_checked(
        self, request: DraftRequest
    ) -> tuple[list[QuestionContent], CheckOutput]:
        """Draft, check, and allow exactly one revision. Raises LlmError/ValidationError."""
        contents = await self._draft(request, hint=None)
        verdict = await self._check(contents)
        if verdict.verdict == "revise":
            contents = await self._draft(request, hint=verdict.revision_hint)
            verdict = await self._check(contents)
            if verdict.verdict == "revise":
                verdict = CheckOutput(verdict="reject", reason=verdict.reason)
        return contents, verdict

    async def store(
        self, contents: list[QuestionContent], verdict: CheckOutput, report: DraftingReport
    ) -> None:
        for content in contents:
            question = await self._questions.create(content)
            if verdict.verdict != "ok":
                await service.reject(
                    self._questions, question.id, reason=f"Automatic check: {verdict.reason}"
                )
        if verdict.verdict == "ok":
            report.drafts += 1
        else:
            report.rejected += 1


async def existing_texts(questions: QuestionRepository, *, limit: int = 100) -> list[str]:
    return [
        question.text
        for question in await questions.list()
        if question.status is not QuestionStatus.RETIRED
    ][:limit]
