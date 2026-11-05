from typing import Annotated

from fastapi import Depends
from psycopg_pool import AsyncConnectionPool

from dicrates.core.db import get_db_pool
from dicrates.questions.repository import PostgresQuestionRepository, QuestionRepository


def get_question_repository(
    pool: Annotated[AsyncConnectionPool, Depends(get_db_pool)],
) -> QuestionRepository:
    return PostgresQuestionRepository(pool)


Questions = Annotated[QuestionRepository, Depends(get_question_repository)]
