"""Curated news feeds: configuration, fetching, parsing and storage of feed entries."""

import html
import logging
import re
import tomllib
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import struct_time
from typing import Any, Protocol, cast
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import feedparser  # pyright: ignore[reportMissingTypeStubs]
import httpx
from pydantic import BaseModel, ConfigDict

from dicrates.core.language import Language
from dicrates.news.models import NewsItem

logger = logging.getLogger(__name__)

SOURCES_FILE = Path(__file__).resolve().parents[3] / "config" / "news_sources.toml"
ITEM_LIFETIME = timedelta(days=7)
MAX_SUMMARY_LENGTH = 500
_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")


class NewsSource(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    url: str
    language: Language
    #: Rough political orientation, to keep the source list balanced.
    leaning: str
    terms_note: str = ""


def load_sources(path: Path = SOURCES_FILE) -> list[NewsSource]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return [NewsSource.model_validate(entry) for entry in data["sources"]]


class FeedFetchError(Exception):
    pass


class FeedParseError(Exception):
    pass


class FeedFetcher(Protocol):
    async def fetch(self, url: str) -> bytes: ...


class HttpxFeedFetcher:
    def __init__(self, *, timeout: float = 15.0) -> None:
        self._timeout = timeout

    async def fetch(self, url: str) -> bytes:
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=True,
                headers={"User-Agent": "Dicrates-NewsReader/0.1 (feed reader)"},
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except httpx.HTTPError as error:
            raise FeedFetchError(f"{url}: {type(error).__name__}") from None


class NewsRepository(Protocol):
    async def add_new(self, items: list[NewsItem]) -> int: ...

    async def delete_expired(self, now: datetime) -> int: ...

    async def recent(self, *, limit: int) -> list[NewsItem]: ...


def _plain_text(value: str) -> str:
    text = _SPACE.sub(" ", html.unescape(_TAG.sub(" ", value))).strip()
    if len(text) <= MAX_SUMMARY_LENGTH:
        return text
    return text[: MAX_SUMMARY_LENGTH - 1].rsplit(" ", 1)[0] + "…"


def _clean_url(url: str) -> str:
    """Drop tracking parameters and fragments so the same article deduplicates."""
    parts = urlsplit(url.strip())
    query = [(key, value) for key, value in parse_qsl(parts.query) if not key.startswith("utm_")]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))


def _published(entry: dict[str, Any], fallback: datetime) -> datetime:
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if isinstance(value, struct_time):
            return datetime(*value[:6], tzinfo=UTC)
    return fallback


def parse_feed(raw: bytes, source: NewsSource, *, now: datetime) -> list[NewsItem]:
    parsed = cast("dict[str, Any]", feedparser.parse(raw))  # pyright: ignore[reportUnknownMemberType]
    entries = cast("list[dict[str, Any]]", parsed.get("entries") or [])
    if not parsed.get("version"):  # neither RSS nor Atom (e.g. an HTML error page)
        msg = f"{source.name}: not a valid feed"
        raise FeedParseError(msg)
    items: list[NewsItem] = []
    for entry in entries:
        link = entry.get("link")
        title = entry.get("title")
        if not isinstance(link, str) or not isinstance(title, str) or not link.startswith("http"):
            continue
        summary = entry.get("summary")
        items.append(
            NewsItem(
                url=_clean_url(link),
                title=_plain_text(title),
                summary=_plain_text(summary) if isinstance(summary, str) else "",
                outlet=source.name,
                language=source.language,
                leaning=source.leaning,
                published_at=_published(entry, now),
                expires_at=now + ITEM_LIFETIME,
            )
        )
    return items


@dataclass
class CollectReport:
    added: int = 0
    expired: int = 0
    failed_sources: list[str] = field(default_factory=list[str])


async def collect_news(
    sources: list[NewsSource],
    fetcher: FeedFetcher,
    repository: NewsRepository,
    *,
    now: datetime,
) -> CollectReport:
    """Fetch all feeds, store new entries (deduplicated by URL), drop expired ones."""
    report = CollectReport()
    for source in sources:
        try:
            items = parse_feed(await fetcher.fetch(source.url), source, now=now)
        except (FeedFetchError, FeedParseError) as error:
            logger.warning("skipping news source %s: %s", source.name, type(error).__name__)
            report.failed_sources.append(source.name)
            continue
        report.added += await repository.add_new(items)
    report.expired = await repository.delete_expired(now)
    return report
