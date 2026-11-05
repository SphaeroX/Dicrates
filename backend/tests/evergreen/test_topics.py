from pathlib import Path

import pytest
from pydantic import ValidationError

from dicrates.evergreen.topics import EvergreenTopic, TopicKind, load_topics

VALID = """
[[topics]]
id = "speed_limit"
title = "General speed limit on German motorways"
topic_area = "environment"
kind = "evergreen"
guiding_question = "Should Germany introduce a general speed limit on motorways?"
sources = [
  { url = "https://de.wikipedia.org/wiki/Tempolimit", title = "Tempolimit", outlet = "Wikipedia" },
]
"""


def test_loads_a_valid_topic(tmp_path: Path) -> None:
    path = tmp_path / "topics.toml"
    path.write_text(VALID, encoding="utf-8")

    [topic] = load_topics(path)

    assert topic.id == "speed_limit"
    assert topic.kind is TopicKind.EVERGREEN
    assert topic.sources[0].outlet == "Wikipedia"


def test_unknown_topic_area_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "topics.toml"
    path.write_text(VALID.replace('"environment"', '"astrology"'), encoding="utf-8")

    with pytest.raises(ValidationError):
        load_topics(path)


def test_sources_are_required() -> None:
    with pytest.raises(ValidationError):
        EvergreenTopic.model_validate(
            {"id": "x", "title": "X", "topic_area": "society", "kind": "evergreen", "sources": []}
        )


def test_ids_must_be_unique(tmp_path: Path) -> None:
    path = tmp_path / "topics.toml"
    path.write_text(VALID + VALID, encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate"):
        load_topics(path)


def test_curated_list_is_broad_and_valid() -> None:
    topics = load_topics()

    assert len(topics) >= 40
    assert {topic.kind for topic in topics} == {TopicKind.EVERGREEN, TopicKind.HISTORICAL}
    assert len({topic.topic_area for topic in topics}) >= 8
    assert all(str(source.url).startswith("https://") for t in topics for source in t.sources)
