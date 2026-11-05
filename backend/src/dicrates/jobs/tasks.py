"""Job definitions. Every job must be idempotent (safe to retry) and take only ids."""

import logging

from dicrates.core.db import create_pool
from dicrates.core.settings import get_settings
from dicrates.jobs.app import app
from dicrates.news.cycle import run_news_cycle

logger = logging.getLogger(__name__)

NEWS_QUESTIONS_PER_CYCLE = 3


@app.task(name="ping")
def ping(message: str) -> str:
    """Example job proving that enqueueing and execution work."""
    return f"pong: {message}"


@app.periodic(cron="17 */6 * * *")
@app.task(name="news_questions", queueing_lock="news_questions")
async def news_questions(timestamp: int) -> None:
    """Every 6 hours: fetch the news feeds and draft new questions for operator review."""
    del timestamp
    settings = get_settings()
    if settings.database_url is None:
        logger.warning("news_questions skipped: DATABASE_URL is not set")
        return
    async with create_pool(settings.database_url.get_secret_value(), max_size=2) as pool:
        report = await run_news_cycle(pool, settings, limit=NEWS_QUESTIONS_PER_CYCLE)
    logger.info(
        "news_questions: %d new items, %d drafts, %d rejected, %d discarded, failed feeds: %s",
        report.collected.added,
        report.generated.drafts,
        report.generated.rejected,
        report.generated.discarded,
        ", ".join(report.collected.failed_sources) or "none",
    )
