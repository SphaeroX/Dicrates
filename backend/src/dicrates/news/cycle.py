"""One full news cycle with real dependencies (used by the periodic job and the CLI)."""

from dataclasses import dataclass
from datetime import UTC, datetime

from psycopg_pool import AsyncConnectionPool

from dicrates.core.settings import Settings
from dicrates.llm.call_log import PostgresLlmCallLog
from dicrates.llm.factory import build_model
from dicrates.llm.runner import LlmRunner
from dicrates.news.pipeline import PipelineReport, generate_from_news
from dicrates.news.repository import PostgresNewsRepository
from dicrates.news.sources import (
    CollectReport,
    FeedFetcher,
    HttpxFeedFetcher,
    collect_news,
    load_sources,
)
from dicrates.questions.repository import PostgresQuestionRepository


@dataclass
class NewsCycleReport:
    collected: CollectReport
    generated: PipelineReport


async def run_news_cycle(
    pool: AsyncConnectionPool,
    settings: Settings,
    *,
    limit: int,
    fetcher: FeedFetcher | None = None,
) -> NewsCycleReport:
    news = PostgresNewsRepository(pool)
    collected = await collect_news(
        load_sources(), fetcher or HttpxFeedFetcher(), news, now=datetime.now(UTC)
    )
    runner = LlmRunner(
        build_model(settings),
        model_id=str(settings.llm_model),
        call_log=PostgresLlmCallLog(pool),
    )
    generated = await generate_from_news(
        runner=runner, news=news, questions=PostgresQuestionRepository(pool), limit=limit
    )
    return NewsCycleReport(collected=collected, generated=generated)
