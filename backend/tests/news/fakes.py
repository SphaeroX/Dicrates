from datetime import datetime
from pathlib import Path

from dicrates.news.models import NewsItem
from dicrates.news.sources import FeedFetchError

FIXTURES = Path(__file__).parent / "fixtures"


class FakeFeedFetcher:
    """Serves fixture files by URL; unknown URLs fail like a network error."""

    def __init__(self, feeds: dict[str, str]) -> None:
        self.feeds = feeds
        self.requested: list[str] = []

    async def fetch(self, url: str) -> bytes:
        self.requested.append(url)
        if url not in self.feeds:
            raise FeedFetchError(url)
        return (FIXTURES / self.feeds[url]).read_bytes()


class FakeNewsRepository:
    def __init__(self) -> None:
        self.items: dict[str, NewsItem] = {}

    async def add_new(self, items: list[NewsItem]) -> int:
        added = 0
        for item in items:
            if item.url not in self.items:
                self.items[item.url] = item
                added += 1
        return added

    async def delete_expired(self, now: datetime) -> int:
        expired = [url for url, item in self.items.items() if item.expires_at <= now]
        for url in expired:
            del self.items[url]
        return len(expired)

    async def recent(self, *, limit: int) -> list[NewsItem]:
        newest = sorted(self.items.values(), key=lambda item: item.published_at, reverse=True)
        return newest[:limit]
