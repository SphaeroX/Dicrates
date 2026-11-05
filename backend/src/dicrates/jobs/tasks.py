"""Job definitions. Every job must be idempotent (safe to retry)."""

from dicrates.jobs.app import app


@app.task(name="ping")
def ping(message: str) -> str:
    """Example job proving that enqueueing and execution work."""
    return f"pong: {message}"
