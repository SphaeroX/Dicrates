import asyncio
import json
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
import typer
from tests.questions.factories import content_data, make_content
from tests.questions.fakes import FakeQuestionRepository
from typer.testing import CliRunner

from dicrates.admin.cli import make_app
from dicrates.news.cycle import NewsCycleReport
from dicrates.news.pipeline import PipelineReport
from dicrates.news.sources import CollectReport
from dicrates.questions.models import QuestionStatus
from dicrates.questions.repository import QuestionRepository

runner = CliRunner()


@pytest.fixture
def repository() -> FakeQuestionRepository:
    return FakeQuestionRepository()


@pytest.fixture
def cli(repository: FakeQuestionRepository) -> typer.Typer:
    @asynccontextmanager
    async def factory() -> AsyncGenerator[QuestionRepository]:
        yield repository

    return make_app(questions_repository=factory)


def create(repository: FakeQuestionRepository, **overrides: object) -> str:
    return str(asyncio.run(repository.create(make_content(**overrides))).id)


def test_list_by_status(cli: typer.Typer, repository: FakeQuestionRepository) -> None:
    draft_id = create(repository)
    approved_id = create(repository)
    asyncio.run(repository.set_status(uuid.UUID(approved_id), QuestionStatus.APPROVED))

    result = runner.invoke(cli, ["questions", "list", "--status", "draft"])

    assert result.exit_code == 0, result.output
    assert draft_id in result.output
    assert approved_id not in result.output


def test_show_prints_the_full_question(
    cli: typer.Typer, repository: FakeQuestionRepository
) -> None:
    question_id = create(repository)

    result = runner.invoke(cli, ["questions", "show", question_id])

    assert result.exit_code == 0, result.output
    assert "Exampleville Gazette" in result.output
    assert "car-free market square" in result.output


def test_approve(cli: typer.Typer, repository: FakeQuestionRepository) -> None:
    question_id = create(repository)

    result = runner.invoke(cli, ["questions", "approve", question_id])

    assert result.exit_code == 0, result.output
    [question] = repository.questions.values()
    assert question.status is QuestionStatus.APPROVED


def test_reject_needs_a_reason(cli: typer.Typer, repository: FakeQuestionRepository) -> None:
    question_id = create(repository)

    missing = runner.invoke(cli, ["questions", "reject", question_id])
    result = runner.invoke(cli, ["questions", "reject", question_id, "--reason", "Leading"])

    assert missing.exit_code != 0
    assert result.exit_code == 0, result.output
    [question] = repository.questions.values()
    assert question.status is QuestionStatus.REJECTED
    assert question.rejection_reason == "Leading"


def test_retire_a_draft_fails_cleanly(cli: typer.Typer, repository: FakeQuestionRepository) -> None:
    question_id = create(repository)

    result = runner.invoke(cli, ["questions", "retire", question_id])

    assert result.exit_code == 1
    assert "draft" in result.output


def test_unknown_id_fails_cleanly(cli: typer.Typer) -> None:
    result = runner.invoke(cli, ["questions", "approve", "00000000-0000-4000-8000-000000000000"])

    assert result.exit_code == 1
    assert "not found" in result.output


def test_edit_text_and_options(cli: typer.Typer, repository: FakeQuestionRepository) -> None:
    question_id = create(repository)

    result = runner.invoke(
        cli, ["questions", "edit", question_id, "--text", "Should Exampleville ban cars?"]
    )

    assert result.exit_code == 0, result.output
    [question] = repository.questions.values()
    assert question.text == "Should Exampleville ban cars?"


def test_edit_facts_from_file(
    cli: typer.Typer,
    repository: FakeQuestionRepository,
    tmp_path: Path,
) -> None:
    question_id = create(repository)
    data = content_data()
    path = tmp_path / "content.json"
    path.write_text(
        json.dumps(
            {
                "facts": [{"text": "Corrected invented fact.", "source_ids": [2]}],
                "sources": data["sources"],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(cli, ["questions", "edit", question_id, "--content-file", str(path)])

    assert result.exit_code == 0, result.output
    [question] = repository.questions.values()
    assert [fact.text for fact in question.facts] == ["Corrected invented fact."]


def test_import_creates_a_draft(
    cli: typer.Typer,
    repository: FakeQuestionRepository,
    tmp_path: Path,
) -> None:
    path = tmp_path / "question.json"
    path.write_text(json.dumps(content_data(origin="evergreen")), encoding="utf-8")

    result = runner.invoke(cli, ["questions", "import", str(path)])

    assert result.exit_code == 0, result.output
    [question] = repository.questions.values()
    assert question.status is QuestionStatus.DRAFT


def test_list_marks_single_source_questions(
    cli: typer.Typer, repository: FakeQuestionRepository
) -> None:
    single_id = create(
        repository,
        facts=[{"text": "Invented fact.", "source_ids": [1]}],
        sources=[content_data()["sources"][0]],
    )

    result = runner.invoke(cli, ["questions", "list"])

    line = next(line for line in result.output.splitlines() if single_id in line)
    assert "[single source]" in line


def test_generate_from_news_runs_one_cycle(repository: FakeQuestionRepository) -> None:
    limits: list[int] = []

    async def fake_cycle(limit: int) -> NewsCycleReport:
        limits.append(limit)
        return NewsCycleReport(
            collected=CollectReport(added=12, expired=1, failed_sources=["Offline Daily"]),
            generated=PipelineReport(drafts=2, rejected=1, discarded=0),
        )

    @asynccontextmanager
    async def factory() -> AsyncGenerator[QuestionRepository]:
        yield repository

    cli = make_app(questions_repository=factory, news_cycle=fake_cycle)

    result = runner.invoke(cli, ["questions", "generate", "--from-news", "--limit", "3"])

    assert result.exit_code == 0, result.output
    assert limits == [3]
    assert "2 draft(s)" in result.output
    assert "Offline Daily" in result.output


def test_generate_needs_a_source_flag(cli: typer.Typer) -> None:
    result = runner.invoke(cli, ["questions", "generate"])

    assert result.exit_code != 0
