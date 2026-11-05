"""The Procrastinate app. Jobs share the Postgres database with the API."""

from procrastinate import App, PsycopgConnector

from dicrates.core.settings import get_settings


def _conninfo() -> str:
    database_url = get_settings().database_url
    # Empty conninfo falls back to libpq defaults (PGHOST, ...), useful for tooling.
    return database_url.get_secret_value() if database_url else ""


app = App(
    connector=PsycopgConnector(conninfo=_conninfo()),
    import_paths=["dicrates.jobs.tasks", "dicrates.rounds.jobs"],
)
