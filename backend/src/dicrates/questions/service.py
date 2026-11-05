"""Operator actions on questions; every status change goes through `ensure_transition`."""

import uuid
from typing import Any

from pydantic import ValidationError

from dicrates.questions.models import (
    InvalidTransitionError,
    Question,
    QuestionContent,
    QuestionStatus,
    ensure_transition,
)
from dicrates.questions.repository import QuestionRepository


class QuestionNotFoundError(LookupError):
    pass


async def _load(repository: QuestionRepository, question_id: uuid.UUID) -> Question:
    question = await repository.get(question_id)
    if question is None:
        msg = f"question {question_id} not found"
        raise QuestionNotFoundError(msg)
    return question


async def _change_status(
    repository: QuestionRepository,
    question_id: uuid.UUID,
    target: QuestionStatus,
    *,
    reason: str | None = None,
) -> Question:
    question = await _load(repository, question_id)
    ensure_transition(question.status, target)
    return await repository.set_status(question_id, target, reason=reason)


async def approve(repository: QuestionRepository, question_id: uuid.UUID) -> Question:
    return await _change_status(repository, question_id, QuestionStatus.APPROVED)


async def reject(
    repository: QuestionRepository, question_id: uuid.UUID, *, reason: str
) -> Question:
    if not reason.strip():
        msg = "a rejection needs a reason"
        raise ValueError(msg)
    return await _change_status(
        repository, question_id, QuestionStatus.REJECTED, reason=reason.strip()
    )


async def retire(repository: QuestionRepository, question_id: uuid.UUID) -> Question:
    return await _change_status(repository, question_id, QuestionStatus.RETIRED)


async def edit(repository: QuestionRepository, question_id: uuid.UUID, **changes: Any) -> Question:
    """Correct a draft before approval; the changed content is validated again."""
    question = await _load(repository, question_id)
    if question.status is not QuestionStatus.DRAFT:
        msg = f"only draft questions can be edited, this one is {question.status}"
        raise InvalidTransitionError(msg)
    data = question.model_dump(include=set(QuestionContent.model_fields))
    data.update(changes)
    try:
        content = QuestionContent.model_validate(data)
    except ValidationError as error:
        raise ValueError(str(error)) from None
    return await repository.update_content(question_id, content)
