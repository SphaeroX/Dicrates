import uuid
from typing import Any, Protocol

from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import AsyncConnectionPool

from dicrates.core.language import Language
from dicrates.questions.models import Question, QuestionContent, QuestionStatus


class QuestionRepository(Protocol):
    async def create(self, content: QuestionContent) -> Question: ...

    async def get(self, question_id: uuid.UUID) -> Question | None: ...

    async def list(
        self,
        *,
        status: QuestionStatus | None = None,
        language: Language | None = None,
        topic_area: str | None = None,
    ) -> list[Question]: ...

    async def set_status(
        self, question_id: uuid.UUID, status: QuestionStatus, *, reason: str | None = None
    ) -> Question: ...

    async def update_content(
        self, question_id: uuid.UUID, content: QuestionContent
    ) -> Question: ...


_COLUMNS = sql.SQL(
    "id, language, format, text, option_a, option_b, facts, sources, topic_area, origin,"
    " prompt_version, group_id, topic_key, review_notes, status, rejection_reason,"
    " created_at, updated_at"
)


def _content_params(content: QuestionContent) -> dict[str, Any]:
    data = content.model_dump(mode="json")
    return {
        **data,
        "facts": Jsonb(data["facts"]),
        "sources": Jsonb(data["sources"]),
        "review_notes": Jsonb(data["review_notes"]),
    }


def _question(row: dict[str, Any] | None) -> Question:
    if row is None:
        msg = "question not found"
        raise LookupError(msg)
    return Question.model_validate(row)


class PostgresQuestionRepository:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._pool = pool

    async def _one(self, template: str, params: dict[str, Any]) -> dict[str, Any] | None:
        query = sql.SQL(template).format(columns=_COLUMNS)  # pyright: ignore[reportArgumentType]
        async with self._pool.connection() as connection:
            cursor = connection.cursor(row_factory=dict_row)
            await cursor.execute(query, params)
            return await cursor.fetchone()

    async def create(self, content: QuestionContent) -> Question:
        row = await self._one(
            "INSERT INTO public.questions (language, format, text, option_a, option_b, facts,"
            " sources, topic_area, origin, prompt_version, group_id, topic_key, review_notes)"
            " VALUES (%(language)s, %(format)s,"
            " %(text)s, %(option_a)s, %(option_b)s, %(facts)s, %(sources)s, %(topic_area)s,"
            " %(origin)s, %(prompt_version)s, %(group_id)s, %(topic_key)s, %(review_notes)s)"
            " RETURNING {columns}",
            _content_params(content),
        )
        return _question(row)

    async def get(self, question_id: uuid.UUID) -> Question | None:
        row = await self._one(
            "SELECT {columns} FROM public.questions WHERE id = %(id)s",
            {"id": question_id},
        )
        return None if row is None else _question(row)

    async def list(
        self,
        *,
        status: QuestionStatus | None = None,
        language: Language | None = None,
        topic_area: str | None = None,
    ) -> list[Question]:
        async with self._pool.connection() as connection:
            cursor = connection.cursor(row_factory=dict_row)
            query = sql.SQL(
                "SELECT {columns} FROM public.questions"
                " WHERE (%(status)s::text IS NULL OR status = %(status)s)"
                " AND (%(language)s::text IS NULL OR language = %(language)s)"
                " AND (%(topic_area)s::text IS NULL OR topic_area = %(topic_area)s)"
                " ORDER BY created_at DESC, id"
            ).format(columns=_COLUMNS)
            await cursor.execute(
                query, {"status": status, "language": language, "topic_area": topic_area}
            )
            return [_question(row) for row in await cursor.fetchall()]

    async def set_status(
        self, question_id: uuid.UUID, status: QuestionStatus, *, reason: str | None = None
    ) -> Question:
        row = await self._one(
            "UPDATE public.questions SET status = %(status)s, rejection_reason = %(reason)s,"
            " updated_at = now() WHERE id = %(id)s RETURNING {columns}",
            {"id": question_id, "status": status, "reason": reason},
        )
        return _question(row)

    async def update_content(self, question_id: uuid.UUID, content: QuestionContent) -> Question:
        row = await self._one(
            "UPDATE public.questions SET language = %(language)s, format = %(format)s,"
            " text = %(text)s, option_a = %(option_a)s, option_b = %(option_b)s,"
            " facts = %(facts)s, sources = %(sources)s, topic_area = %(topic_area)s,"
            " origin = %(origin)s, prompt_version = %(prompt_version)s, group_id = %(group_id)s,"
            " topic_key = %(topic_key)s, review_notes = %(review_notes)s,"
            " updated_at = now()"
            " WHERE id = %(id)s RETURNING {columns}",
            {**_content_params(content), "id": question_id},
        )
        return _question(row)
