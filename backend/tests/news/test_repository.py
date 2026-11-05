"""PostgresNewsRepository against the local Supabase stack."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from dicrates.core.db import create_pool
from dicrates.core.language import Language
from dicrates.news.models import NewsItem
from dicrates.news.repository import PostgresNewsRepository

pytestmark = pytest.mark.integration

NOW = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)


def news_item(tag: str, *, expires_in: timedelta = timedelta(days=7)) -> NewsItem:
    return NewsItem(
        url=f"https://{tag}.example.test/story",
        title=f"Invented headline {tag}",
        summary="Invented summary.",
        outlet="Exampleville Gazette",
        language=Language.EN,
        leaning="centre",
        published_at=NOW,
        expires_at=NOW + expires_in,
    )


async def test_add_deduplicate_expire(database_url: str) -> None:
    tag = uuid.uuid4().hex[:10]
    fresh = news_item(f"fresh-{tag}")
    old = news_item(f"old-{tag}", expires_in=timedelta(days=-1))

    async with create_pool(database_url, max_size=2) as pool:
        repository = PostgresNewsRepository(pool)
        try:
            assert await repository.add_new([fresh, old]) == 2
            assert await repository.add_new([fresh]) == 0

            assert await repository.delete_expired(NOW) >= 1
            urls = [item.url for item in await repository.recent(limit=500)]
            assert fresh.url in urls
            assert old.url not in urls
        finally:
            async with pool.connection() as connection:
                await connection.execute(
                    "DELETE FROM public.news_items WHERE url LIKE %s", (f"%{tag}%",)
                )
