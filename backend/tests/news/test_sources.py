from datetime import UTC, datetime, timedelta

import pytest
from tests.news.fakes import FIXTURES, FakeFeedFetcher, FakeNewsRepository

from dicrates.core.language import Language
from dicrates.news.sources import (
    FeedParseError,
    NewsSource,
    collect_news,
    load_sources,
    parse_feed,
)

NOW = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)
GAZETTE = NewsSource(
    name="Exampleville Gazette",
    url="https://gazette.example.test/rss",
    language=Language.EN,
    leaning="centre",
)
RADIO = NewsSource(
    name="Regional Radio",
    url="https://radio.example.test/atom",
    language=Language.EN,
    leaning="public broadcaster",
)


def test_parses_rss_items_without_html_and_tracking() -> None:
    items = parse_feed((FIXTURES / "rss_valid.xml").read_bytes(), GAZETTE, now=NOW)

    assert [item.title for item in items] == [
        "Council debates car-free market square",
        "Tram line costs rise again",
    ]
    first = items[0]
    assert first.url == "https://gazette.example.test/news/car-free-square"
    assert first.summary == "The town council of Exampleville discussed closing the square to cars."
    assert first.outlet == "Exampleville Gazette"
    assert first.language is Language.EN
    assert first.published_at == datetime(2026, 11, 4, 8, 30, tzinfo=UTC)
    assert first.expires_at == NOW + timedelta(days=7)


def test_parses_atom_entries() -> None:
    [item] = parse_feed((FIXTURES / "atom_valid.xml").read_bytes(), RADIO, now=NOW)

    assert item.url == "https://radio.example.test/stories/car-free"
    assert item.summary == "Two towns closed their squares to cars in 2025."


def test_long_summaries_are_shortened() -> None:
    raw = (
        (FIXTURES / "rss_valid.xml")
        .read_bytes()
        .replace(b"Invented summary about tram costs.", b"word " * 400)
    )

    items = parse_feed(raw, GAZETTE, now=NOW)

    assert len(items[1].summary) <= 500


def test_broken_feed_raises() -> None:
    with pytest.raises(FeedParseError):
        parse_feed((FIXTURES / "broken.xml").read_bytes(), GAZETTE, now=NOW)


async def test_collect_skips_broken_feeds_and_deduplicates(
    caplog: pytest.LogCaptureFixture,
) -> None:
    broken = NewsSource(
        name="Broken Times",
        url="https://broken.example.test/rss",
        language=Language.EN,
        leaning="x",
    )
    offline = NewsSource(
        name="Offline Daily",
        url="https://offline.example.test/rss",
        language=Language.EN,
        leaning="x",
    )
    fetcher = FakeFeedFetcher(
        {GAZETTE.url: "rss_valid.xml", RADIO.url: "atom_valid.xml", broken.url: "broken.xml"}
    )
    repository = FakeNewsRepository()

    first = await collect_news([GAZETTE, RADIO, broken, offline], fetcher, repository, now=NOW)
    second = await collect_news([GAZETTE], fetcher, repository, now=NOW)

    assert first.added == 3
    assert first.failed_sources == ["Broken Times", "Offline Daily"]
    assert second.added == 0
    assert len(repository.items) == 3
    assert "Broken Times" in caplog.text


async def test_collect_deletes_expired_items() -> None:
    fetcher = FakeFeedFetcher({GAZETTE.url: "rss_valid.xml"})
    repository = FakeNewsRepository()
    await collect_news([GAZETTE], fetcher, repository, now=NOW)

    report = await collect_news([], fetcher, repository, now=NOW + timedelta(days=8))

    assert report.expired == 2
    assert repository.items == {}


def test_configured_sources_load_and_cover_both_languages() -> None:
    sources = load_sources()

    assert {source.language for source in sources} == {Language.EN, Language.DE}
    assert len({source.leaning for source in sources}) >= 3
    assert all(source.url.startswith("https://") for source in sources)
    assert len({source.name for source in sources}) == len(sources)
