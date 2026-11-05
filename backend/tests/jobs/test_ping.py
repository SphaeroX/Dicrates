from typing import Any

import pytest
from procrastinate.testing import InMemoryConnector

from dicrates.jobs import app as jobs_module
from dicrates.jobs.app import app
from dicrates.jobs.tasks import ping


async def test_ping_job_is_enqueued_and_executed() -> None:
    connector = InMemoryConnector()
    with app.replace_connector(connector):
        job_id = await ping.defer_async(message="hello")
        await app.run_worker_async(wait=False)

    statuses = {job["id"]: job["status"] for job in connector.jobs.values()}
    assert statuses[job_id] == "succeeded"


def test_ping_returns_pong() -> None:
    assert ping(message="hello") == "pong: hello"


def test_app_imports_task_module() -> None:
    assert "dicrates.jobs.tasks" in jobs_module.app.import_paths


@pytest.mark.integration
async def test_ping_job_runs_through_postgres(database_url: str) -> None:
    from procrastinate import PsycopgConnector

    connector = PsycopgConnector(conninfo=database_url)
    with app.replace_connector(connector):
        async with app.open_async():
            job_id = await ping.defer_async(message="integration")
            await app.run_worker_async(wait=False)
            jobs = await app.job_manager.list_jobs_async(id=job_id)

    assert [job.status for job in jobs] == ["succeeded"]


def test_news_questions_job_is_periodic() -> None:
    from dicrates.jobs import tasks

    assert tasks.news_questions.name == "news_questions"
    registry: Any = app.periodic_registry
    periodic = [entry.task.name for entry in registry.periodic_tasks.values()]
    assert "news_questions" in periodic
