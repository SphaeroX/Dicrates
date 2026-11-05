import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from dicrates.core.language import Language
from dicrates.profiles.dependencies import ConsentedUser
from dicrates.questions.dependencies import Questions
from dicrates.questions.models import Fact, Question, QuestionFormat, QuestionStatus, Source

router = APIRouter(prefix="/questions", tags=["questions"])


class QuestionOut(BaseModel):
    """What players see: no status, rejection reason or prompt version."""

    id: uuid.UUID
    language: Language
    format: QuestionFormat
    text: str
    option_a: str | None
    option_b: str | None
    facts: list[Fact]
    sources: list[Source]
    topic_area: str

    @classmethod
    def of(cls, question: Question) -> QuestionOut:
        return cls.model_validate(question.model_dump(include=set(cls.model_fields)))


@router.get("")
async def list_questions(
    user: ConsentedUser,
    questions: Questions,
    language: Language,
    topic_area: str | None = None,
) -> list[QuestionOut]:
    """Approved questions to choose from when creating a room."""
    del user
    found = await questions.list(
        status=QuestionStatus.APPROVED, language=language, topic_area=topic_area
    )
    return [QuestionOut.of(question) for question in found]


@router.get("/{question_id}")
async def get_question(
    user: ConsentedUser, questions: Questions, question_id: uuid.UUID
) -> QuestionOut:
    del user
    question = await questions.get(question_id)
    if question is None or question.status is not QuestionStatus.APPROVED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="question_not_found")
    return QuestionOut.of(question)
