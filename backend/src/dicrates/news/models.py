from datetime import datetime

from pydantic import BaseModel, ConfigDict

from dicrates.core.language import Language


class NewsItem(BaseModel):
    """One feed entry. Only feed metadata and the feed's own short text, never full articles."""

    model_config = ConfigDict(frozen=True)

    url: str
    title: str
    summary: str
    outlet: str
    language: Language
    leaning: str
    published_at: datetime
    expires_at: datetime
