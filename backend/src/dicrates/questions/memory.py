"""In-memory question store, used by `generate --output` to write drafts to a file."""

import uuid
from datetime import UTC, datetime

from dicrates.core.language import Language
from dicrates.questions.models import Question, QuestionContent, QuestionStatus


class InMemoryQuestionRepository:
    def __init__(self, contents: list[QuestionContent] | None = None) -> None:
        self.questions: dict[uuid.UUID, Question] = {}
        for content in contents or []:
            self._add(content)

    def _add(self, content: QuestionContent) -> Question:
        now = datetime.now(UTC)
        question = Question.model_validate(
            {
                **content.model_dump(),
                "id": uuid.uuid4(),
                "status": QuestionStatus.DRAFT,
                "rejection_reason": None,
                "created_at": now,
                "updated_at": now,
            }
        )
        self.questions[question.id] = question
        return question

    async def create(self, content: QuestionContent) -> Question:
        return self._add(content)

    async def get(self, question_id: uuid.UUID) -> Question | None:
        return self.questions.get(question_id)

    async def list(
        self,
        *,
        status: QuestionStatus | None = None,
        language: Language | None = None,
        topic_area: str | None = None,
    ) -> list[Question]:
        return [
            question
            for question in self.questions.values()
            if (status is None or question.status is status)
            and (language is None or question.language is language)
            and (topic_area is None or question.topic_area == topic_area)
        ]

    async def set_status(
        self, question_id: uuid.UUID, status: QuestionStatus, *, reason: str | None = None
    ) -> Question:
        question = Question.model_validate(
            {
                **self.questions[question_id].model_dump(),
                "status": status,
                "rejection_reason": reason,
                "updated_at": datetime.now(UTC),
            }
        )
        self.questions[question_id] = question
        return question

    async def update_content(self, question_id: uuid.UUID, content: QuestionContent) -> Question:
        question = Question.model_validate(
            {
                **self.questions[question_id].model_dump(),
                **content.model_dump(),
                "updated_at": datetime.now(UTC),
            }
        )
        self.questions[question_id] = question
        return question

    def drafts(self) -> list[QuestionContent]:
        """Draft contents only (rejected ones are not worth importing)."""
        fields = set(QuestionContent.model_fields)
        return [
            QuestionContent.model_validate(question.model_dump(include=fields))
            for question in self.questions.values()
            if question.status is QuestionStatus.DRAFT
        ]
