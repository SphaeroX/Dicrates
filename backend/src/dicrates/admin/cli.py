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
from typing import Annotated, Any, cast

import typer
from pydantic import ValidationError

from dicrates.core.db import create_pool
from dicrates.core.settings import get_settings
from dicrates.evergreen.pipeline import generate_evergreen
from dicrates.evergreen.topics import load_topics
from dicrates.evergreen.url_check import HttpxUrlChecker
from dicrates.llm.call_log import LlmCallLog, LlmCallRecord, PostgresLlmCallLog
from dicrates.llm.factory import LlmConfigurationError, build_model
from dicrates.llm.runner import LlmRunner
from dicrates.news.cycle import NewsCycleReport, run_news_cycle
from dicrates.questions import service
from dicrates.questions.drafting import DraftingReport
from dicrates.questions.memory import InMemoryQuestionRepository
from dicrates.questions.models import Question, QuestionContent, QuestionStatus
from dicrates.questions.repository import PostgresQuestionRepository, QuestionRepository

type RepositoryFactory = Callable[[], AbstractAsyncContextManager[QuestionRepository]]
type NewsCycle = Callable[[int], Coroutine[Any, Any, NewsCycleReport]]
type Evergreen = Callable[
    [QuestionRepository, str | None, int], Coroutine[Any, Any, DraftingReport]
]


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


async def real_evergreen(
    questions: QuestionRepository, topic: str | None, limit: int
) -> DraftingReport:
    """Draft evergreen questions; LLM usage goes to `llm_calls` when a DB is set."""
    settings = get_settings()
    model = build_model(settings)

    async def go(call_log: LlmCallLog) -> DraftingReport:
        runner = LlmRunner(model, model_id=str(settings.llm_model), call_log=call_log)
        return await generate_evergreen(
            runner=runner,
            questions=questions,
            url_checker=HttpxUrlChecker(),
            topics=load_topics(),
            limit=limit,
            topic_id=topic,
        )

    if settings.database_url is None:
        return await go(_PrintingCallLog())
    async with create_pool(settings.database_url.get_secret_value(), max_size=2) as pool:
        return await go(PostgresLlmCallLog(pool))


class _PrintingCallLog:
    """Without a database: print the text-free usage record instead of storing it."""

    async def record(self, entry: LlmCallRecord) -> None:
        typer.echo(
            f"  llm {entry.task}: {'ok' if entry.success else entry.error_kind}, "
            f"{entry.input_tokens}/{entry.output_tokens} tokens, {entry.duration_ms} ms"
        )


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
        + ("  [check notes]" if question.review_notes else "")
    )


def make_app(
    *,
    questions_repository: RepositoryFactory = postgres_questions,
    news_cycle: NewsCycle = postgres_news_cycle,
    evergreen: Evergreen = real_evergreen,
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
        """Create drafts from a JSON file: one question object or a list of them."""
        try:
            contents = _read_contents(path)
        except (ValidationError, ValueError) as error:
            typer.echo(f"Error: {error}", err=True)
            raise typer.Exit(code=1) from None

        async def create_all(repository: QuestionRepository) -> list[Question]:
            return [await repository.create(content) for content in contents]

        for question in with_repository(create_all):
            report(question)

    @questions.command("generate")
    def generate(  # pyright: ignore[reportUnusedFunction]
        from_news: Annotated[
            bool, typer.Option("--from-news", help="Draft questions from the news feeds.")
        ] = False,
        use_evergreen: Annotated[
            bool, typer.Option("--evergreen", help="Draft from the curated topic list.")
        ] = False,
        topic: Annotated[str | None, typer.Option(help="Only this evergreen topic id.")] = None,
        limit: Annotated[int, typer.Option(min=1, max=50, help="Maximum new questions.")] = 3,
        output: Annotated[
            Path | None,
            typer.Option(help="Evergreen only: write drafts to this JSON file instead of the DB."),
        ] = None,
    ) -> None:
        """Let the LLM draft questions (review them with `list`)."""
        if from_news == use_evergreen:
            raise typer.BadParameter("choose exactly one source: --from-news or --evergreen")
        if use_evergreen:
            _generate_evergreen(topic, limit, output)
            return
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

    def _generate_evergreen(topic: str | None, limit: int, output: Path | None) -> None:
        def show(result: DraftingReport) -> None:
            typer.echo(
                f"Questions: {result.drafts} draft(s), {result.rejected} rejected by the"
                f" automatic check, {result.discarded} discarded, {result.skipped} skipped"
                " (already exist)"
            )

        try:
            if output is None:
                show(with_repository(lambda repository: evergreen(repository, topic, limit)))
                return
            # File mode: resume from an existing file, append new drafts.
            existing = _read_contents(output) if output.exists() else []
            memory = InMemoryQuestionRepository(existing)
            show(run(evergreen(memory, topic, limit)))
            drafts = memory.drafts()
            output.write_text(
                json.dumps(
                    [content.model_dump(mode="json") for content in drafts],
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            typer.echo(f"Wrote {len(drafts)} draft(s) to {output}")
        except LlmConfigurationError as error:
            typer.echo(f"Error: {error}", err=True)
            raise typer.Exit(code=1) from None

    return app


def _read_contents(path: Path) -> list[QuestionContent]:
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    items = cast("list[Any]", data) if isinstance(data, list) else [data]
    return [QuestionContent.model_validate(item) for item in items]


app = make_app()


def main() -> None:
    app()
