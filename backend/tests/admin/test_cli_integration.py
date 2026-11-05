"""`dicrates-admin` against the real database (DATABASE_URL)."""

import json
import uuid
from pathlib import Path

import psycopg
import pytest
from tests.questions.factories import content_data
from typer.testing import CliRunner

from dicrates.admin.cli import app
from dicrates.core.settings import get_settings

pytestmark = pytest.mark.integration

runner = CliRunner()


@pytest.fixture(autouse=True)
def database_env(monkeypatch: pytest.MonkeyPatch, database_url: str) -> None:
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()


def import_question(tmp_path: Path, **overrides: object) -> uuid.UUID:
    path = tmp_path / "question.json"
    path.write_text(json.dumps(content_data(**overrides)), encoding="utf-8")
    result = runner.invoke(app, ["questions", "import", str(path)])
    assert result.exit_code == 0, result.output
    return uuid.UUID(result.output.split()[0])


def delete(database_url: str, question_id: uuid.UUID) -> None:
    with psycopg.connect(database_url) as connection:
        connection.execute("DELETE FROM public.questions WHERE id = %s", (question_id,))


def test_import_list_approve_retire(tmp_path: Path, database_url: str) -> None:
    question_id = import_question(tmp_path, topic_area="health")
    try:
        listed = runner.invoke(app, ["questions", "list", "--status", "draft"])
        approved = runner.invoke(app, ["questions", "approve", str(question_id)])
        retired = runner.invoke(app, ["questions", "retire", str(question_id)])

        assert str(question_id) in listed.output
        assert approved.exit_code == 0, approved.output
        assert "approved" in approved.output
        assert retired.exit_code == 0, retired.output
        assert "retired" in retired.output
    finally:
        delete(database_url, question_id)


def test_reject_with_reason(tmp_path: Path, database_url: str) -> None:
    question_id = import_question(tmp_path)
    try:
        result = runner.invoke(
            app, ["questions", "reject", str(question_id), "--reason", "Not neutral"]
        )

        assert result.exit_code == 0, result.output
        with psycopg.connect(database_url) as connection:
            row = connection.execute(
                "SELECT status, rejection_reason FROM public.questions WHERE id = %s",
                (question_id,),
            ).fetchone()
        assert row == ("rejected", "Not neutral")
    finally:
        delete(database_url, question_id)
