"""`dicrates-admin`: operator commands against the database in `DATABASE_URL`.

Example: `uv run dicrates-admin questions list --status draft`.
"""

import asyncio
import json
import selectors
import sys
import uuid
from collections.abc import AsyncGenerator, Callable, Coroutine
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from pathlib import Path
from typing import Annotated, Any

import typer
from pydantic import ValidationError

from dicrates.core.db import create_pool
from dicrates.core.settings import get_settings
from dicrates.llm.factory import LlmConfigurationError
from dicrates.news.cycle import NewsCycleReport, run_news_cycle
from dicrates.questions import service
from dicrates.questions.models import Question, QuestionContent, QuestionStatus
from dicrates.questions.repository import PostgresQuestionRepository, QuestionRepository

type RepositoryFactory = Callable[[], AbstractAsyncContextManager[QuestionRepository]]
type NewsCycle = Callable[[int], Coroutine[Any, Any, NewsCycleReport]]


@asynccontextmanager
async def postgres_questions() -> AsyncGenerator[QuestionRepository]:
    database_url = get_settings().database_url
    if database_url is None:
        raise typer.BadParameter("DATABASE_URL is not set")
    async with create_pool(database_url.get_secret_value(), max_size=2) as pool:
        yield PostgresQuestionRepository(pool)


async def postgres_news_cycle(limit: int) -> NewsCycleReport:
    settings = get_settings()
    if settings.database_url is None:
        raise typer.BadParameter("DATABASE_URL is not set")
    async with create_pool(settings.database_url.get_secret_value(), max_size=2) as pool:
        return await run_news_cycle(pool, settings, limit=limit)


def run[T](coroutine: Coroutine[Any, Any, T]) -> T:
    # psycopg async cannot use the Windows Proactor event loop.
    if sys.platform == "win32":
        return asyncio.run(
            coroutine, loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
        )
    return asyncio.run(coroutine)


def _summary(question: Question) -> str:
    text = question.text if len(question.text) <= 70 else question.text[:67] + "..."
    return (
        f"{question.id}  {question.status:<8}  {question.language}  "
        f"{question.format:<8}  {question.topic_area:<12}  {text}"
        + ("  [single source]" if question.single_source else "")
    )


def make_app(
    *,
    questions_repository: RepositoryFactory = postgres_questions,
    news_cycle: NewsCycle = postgres_news_cycle,
) -> typer.Typer:
    app = typer.Typer(help="Dicrates operator tools.", no_args_is_help=True)
    questions = typer.Typer(help="Review and manage the question library.", no_args_is_help=True)
    app.add_typer(questions, name="questions")

    def with_repository[T](action: Callable[[QuestionRepository], Coroutine[Any, Any, T]]) -> T:
        async def go() -> T:
            async with questions_repository() as repository:
                return await action(repository)

        try:
            return run(go())
        except (service.QuestionNotFoundError, ValueError) as error:
            typer.echo(f"Error: {error}", err=True)
            raise typer.Exit(code=1) from None

    def report(question: Question) -> None:
        typer.echo(_summary(question))

    @questions.command("list")
    def list_questions(  # pyright: ignore[reportUnusedFunction]
        status: Annotated[QuestionStatus | None, typer.Option(help="Only this status.")] = None,
    ) -> None:
        """List questions, newest first."""
        found = with_repository(lambda repository: repository.list(status=status))
        for question in found:
            report(question)
        typer.echo(f"{len(found)} question(s)")

    @questions.command("show")
    def show(question_id: uuid.UUID) -> None:  # pyright: ignore[reportUnusedFunction]
        """Print one question with fact box and sources as JSON."""

        async def load(repository: QuestionRepository) -> Question:
            question = await repository.get(question_id)
            if question is None:
                msg = f"question {question_id} not found"
                raise service.QuestionNotFoundError(msg)
            return question

        question = with_repository(load)
        typer.echo(json.dumps(question.model_dump(mode="json"), indent=2, ensure_ascii=False))

    @questions.command("approve")
    def approve(question_id: uuid.UUID) -> None:  # pyright: ignore[reportUnusedFunction]
        """Release a draft for rooms."""
        report(with_repository(lambda repository: service.approve(repository, question_id)))

    @questions.command("reject")
    def reject(  # pyright: ignore[reportUnusedFunction]
        question_id: uuid.UUID,
        reason: Annotated[str, typer.Option(help="Why the draft is rejected.")],
    ) -> None:
        """Reject a draft with a reason."""
        report(
            with_repository(
                lambda repository: service.reject(repository, question_id, reason=reason)
            )
        )

    @questions.command("retire")
    def retire(question_id: uuid.UUID) -> None:  # pyright: ignore[reportUnusedFunction]
        """Withdraw an approved question (no new rooms)."""
        report(with_repository(lambda repository: service.retire(repository, question_id)))

    @questions.command("edit")
    def edit(  # pyright: ignore[reportUnusedFunction]
        question_id: uuid.UUID,
        text: Annotated[str | None, typer.Option(help="New question text.")] = None,
        option_a: Annotated[str | None, typer.Option(help="Option A (tradeoff).")] = None,
        option_b: Annotated[str | None, typer.Option(help="Option B (tradeoff).")] = None,
        content_file: Annotated[
            Path | None,
            typer.Option(help="JSON file with fields to replace, e.g. facts and sources."),
        ] = None,
    ) -> None:
        """Correct a draft before approval."""
        changes: dict[str, Any] = {}
        if content_file is not None:
            changes.update(json.loads(content_file.read_text(encoding="utf-8")))
        for name, value in (("text", text), ("option_a", option_a), ("option_b", option_b)):
            if value is not None:
                changes[name] = value
        report(with_repository(lambda repository: service.edit(repository, question_id, **changes)))

    @questions.command("import")
    def import_question(path: Path) -> None:  # pyright: ignore[reportUnusedFunction]
        """Create a draft from a JSON file (all question content fields)."""
        try:
            content = QuestionContent.model_validate_json(path.read_text(encoding="utf-8"))
        except ValidationError as error:
            typer.echo(f"Error: {error}", err=True)
            raise typer.Exit(code=1) from None
        report(with_repository(lambda repository: repository.create(content)))

    @questions.command("generate")
    def generate(  # pyright: ignore[reportUnusedFunction]
        from_news: Annotated[
            bool, typer.Option("--from-news", help="Draft questions from the news feeds.")
        ] = False,
        limit: Annotated[int, typer.Option(min=1, max=10, help="Maximum new questions.")] = 3,
    ) -> None:
        """Fetch sources and let the LLM draft questions (review them with `list`)."""
        if not from_news:
            raise typer.BadParameter("choose a source, e.g. --from-news")
        try:
            report = run(news_cycle(limit))
        except LlmConfigurationError as error:
            typer.echo(f"Error: {error}", err=True)
            raise typer.Exit(code=1) from None
        collected, generated = report.collected, report.generated
        typer.echo(f"News: {collected.added} new item(s), {collected.expired} expired")
        if collected.failed_sources:
            typer.echo(f"Failed feeds: {', '.join(collected.failed_sources)}")
        typer.echo(
            f"Questions: {generated.drafts} draft(s), {generated.rejected} rejected by the"
            f" automatic check, {generated.discarded} discarded"
        )

    return app


app = make_app()


def main() -> None:
    app()
