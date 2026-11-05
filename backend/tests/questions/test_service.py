import uuid

import pytest
from tests.questions.factories import make_content
from tests.questions.fakes import FakeQuestionRepository

from dicrates.questions.models import InvalidTransitionError, QuestionStatus
from dicrates.questions.service import (
    QuestionNotFoundError,
    approve,
    edit,
    reject,
    retire,
)


@pytest.fixture
def repository() -> FakeQuestionRepository:
    return FakeQuestionRepository()


async def test_approve_a_draft(repository: FakeQuestionRepository) -> None:
    draft = await repository.create(make_content())

    approved = await approve(repository, draft.id)

    assert approved.status is QuestionStatus.APPROVED


async def test_reject_requires_a_reason(repository: FakeQuestionRepository) -> None:
    draft = await repository.create(make_content())

    with pytest.raises(ValueError, match="reason"):
        await reject(repository, draft.id, reason="  ")

    rejected = await reject(repository, draft.id, reason="Leading wording")
    assert rejected.status is QuestionStatus.REJECTED
    assert rejected.rejection_reason == "Leading wording"


async def test_retire_only_approved(repository: FakeQuestionRepository) -> None:
    draft = await repository.create(make_content())

    with pytest.raises(InvalidTransitionError):
        await retire(repository, draft.id)

    await approve(repository, draft.id)
    assert (await retire(repository, draft.id)).status is QuestionStatus.RETIRED


async def test_unknown_question(repository: FakeQuestionRepository) -> None:
    with pytest.raises(QuestionNotFoundError):
        await approve(repository, uuid.uuid4())


async def test_edit_a_draft_revalidates(repository: FakeQuestionRepository) -> None:
    draft = await repository.create(make_content())

    edited = await edit(repository, draft.id, text="Should Exampleville ban cars on Sundays?")

    assert edited.text == "Should Exampleville ban cars on Sundays?"
    with pytest.raises(ValueError, match="option"):
        await edit(repository, draft.id, option_a="Only A")


async def test_edit_only_drafts(repository: FakeQuestionRepository) -> None:
    draft = await repository.create(make_content())
    await approve(repository, draft.id)

    with pytest.raises(InvalidTransitionError, match="draft"):
        await edit(repository, draft.id, text="Should Exampleville ban cars on Sundays?")
