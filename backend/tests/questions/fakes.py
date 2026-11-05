import uuid
from datetime import UTC, datetime

from dicrates.core.language import Language
from dicrates.questions.models import Question, QuestionContent, QuestionStatus


class FakeQuestionRepository:
    """In-memory `QuestionRepository` for unit tests."""

    def __init__(self) -> None:
        self.questions: dict[uuid.UUID, Question] = {}

    async def create(self, content: QuestionContent) -> Question:
        now = datetime.now(UTC)
        question = Question(
            **content.model_dump(),
            id=uuid.uuid4(),
            status=QuestionStatus.DRAFT,
            rejection_reason=None,
            created_at=now,
            updated_at=now,
        )
        self.questions[question.id] = question
        return question

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
        question = self.questions[question_id].model_copy(
            update={"status": status, "rejection_reason": reason, "updated_at": datetime.now(UTC)}
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
