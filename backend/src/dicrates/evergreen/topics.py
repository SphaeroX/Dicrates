"""Curated list of timeless and historical debate topics (`config/evergreen_topics.toml`)."""

import tomllib
from enum import StrEnum
from pathlib import Path

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from dicrates.questions.drafting import TopicArea

TOPICS_FILE = Path(__file__).resolve().parents[3] / "config" / "evergreen_topics.toml"


class TopicKind(StrEnum):
    EVERGREEN = "evergreen"  # a debate that stays open
    HISTORICAL = "historical"  # decided once; asked again as a question one could decide today


class TopicSource(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    url: AnyHttpUrl
    title: str = Field(min_length=1, max_length=200)
    outlet: str = Field(min_length=1, max_length=200)


class EvergreenTopic(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    title: str = Field(min_length=3, max_length=200)
    topic_area: TopicArea
    kind: TopicKind
    guiding_question: str | None = None
    sources: list[TopicSource] = Field(min_length=1, max_length=6)

    @property
    def topic_key(self) -> str:
        return f"evergreen:{self.id}"


def load_topics(path: Path = TOPICS_FILE) -> list[EvergreenTopic]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    topics = [EvergreenTopic.model_validate(entry) for entry in data["topics"]]
    ids = [topic.id for topic in topics]
    duplicates = sorted({topic_id for topic_id in ids if ids.count(topic_id) > 1})
    if duplicates:
        msg = f"duplicate topic ids: {', '.join(duplicates)}"
        raise ValueError(msg)
    return topics
