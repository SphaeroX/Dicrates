"""PostgresQuestionRepository and RLS on questions against the local Supabase stack."""

import uuid
from collections.abc import AsyncGenerator

import psycopg
import pytest
from psycopg import sql
from tests.questions.factories import make_content, tradeoff_content

from dicrates.core.db import create_pool
from dicrates.core.language import Language
from dicrates.questions import service
from dicrates.questions.models import Question, QuestionContent, QuestionStatus
from dicrates.questions.repository import PostgresQuestionRepository

pytestmark = pytest.mark.integration


class TrackingRepository(PostgresQuestionRepository):
    """Remembers created questions so the test can delete them afterwards."""

    created: list[uuid.UUID]

    async def create(self, content: QuestionContent) -> Question:
        question = await super().create(content)
        self.created.append(question.id)
        return question


@pytest.fixture
async def repository(database_url: str) -> AsyncGenerator[TrackingRepository]:
    async with create_pool(database_url, max_size=2) as pool:
        repository = TrackingRepository(pool)
        repository.created = []
        yield repository
        async with pool.connection() as connection:
            await connection.execute(
                "DELETE FROM public.questions WHERE id = ANY(%s)", (repository.created,)
            )


async def test_create_and_get_round_trip(repository: TrackingRepository) -> None:
    created = await repository.create(tradeoff_content())

    loaded = await repository.get(created.id)
    assert loaded is not None

    assert loaded == created
    assert loaded.status is QuestionStatus.DRAFT
    assert loaded.facts[1].source_ids == [1, 2]
    assert str(loaded.sources[0].url) == "https://example.test/traffic-report"


async def test_list_filters(repository: TrackingRepository) -> None:
    topic = "culture"
    english = await repository.create(make_content(topic_area=topic))
    german = await repository.create(
        make_content(topic_area=topic, language="de", text="Soll Beispielstadt autofrei werden?")
    )
    await service.approve(repository, english.id)

    approved = await repository.list(
        status=QuestionStatus.APPROVED, language=Language.EN, topic_area=topic
    )
    drafts = await repository.list(status=QuestionStatus.DRAFT, topic_area=topic)

    assert [question.id for question in approved] == [english.id]
    assert german.id in [question.id for question in drafts]


async def test_status_workflow(repository: TrackingRepository) -> None:
    question = await repository.create(make_content())

    rejected = await service.reject(repository, question.id, reason="Leading wording")
    with pytest.raises(ValueError, match="rejected"):
        await service.approve(repository, question.id)

    assert rejected.rejection_reason == "Leading wording"


async def test_edit_a_draft(repository: TrackingRepository) -> None:
    question = await repository.create(make_content())

    edited = await service.edit(
        repository, question.id, text="Should Exampleville ban cars on Sundays?"
    )

    assert (await repository.get(question.id)) == edited


async def test_unknown_topic_area_is_rejected_by_the_database(
    repository: TrackingRepository,
) -> None:
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        await repository.create(make_content(topic_area="astrology"))


@pytest.mark.parametrize("role", ["anon", "authenticated"])
@pytest.mark.parametrize("table", ["questions", "topic_areas"])
async def test_clients_cannot_read_questions(
    db_connection: psycopg.AsyncConnection[tuple[object, ...]], role: str, table: str
) -> None:
    await db_connection.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))

    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        await db_connection.execute(
            sql.SQL("SELECT * FROM public.{}").format(sql.Identifier(table))
        )
