import uuid
from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Self

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, StringConstraints, model_validator

from dicrates.core.language import Language

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
FactText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
QuestionText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=10, max_length=300)
]


class QuestionFormat(StrEnum):
    SCALE = "scale"  # for/against on a 5-point scale plus reasoning
    PROPOSAL = "proposal"  # free proposal plus reasoning
    TRADEOFF = "tradeoff"  # what should have priority, A or B?


class QuestionOrigin(StrEnum):
    NEWS = "news"
    EVERGREEN = "evergreen"


class QuestionStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    RETIRED = "retired"


_ALLOWED_TRANSITIONS: dict[QuestionStatus, frozenset[QuestionStatus]] = {
    QuestionStatus.DRAFT: frozenset({QuestionStatus.APPROVED, QuestionStatus.REJECTED}),
    QuestionStatus.APPROVED: frozenset({QuestionStatus.RETIRED}),
}


class InvalidTransitionError(ValueError):
    pass


def ensure_transition(current: QuestionStatus, target: QuestionStatus) -> None:
    if target not in _ALLOWED_TRANSITIONS.get(current, frozenset()):
        msg = f"cannot change a {current} question to {target}"
        raise InvalidTransitionError(msg)


class Source(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: int = Field(ge=1)
    url: AnyHttpUrl
    title: ShortText
    outlet: ShortText
    published_on: date | None = None


class Fact(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    text: FactText
    source_ids: list[int] = Field(min_length=1)


class QuestionContent(BaseModel):
    """Everything a pipeline or the operator writes; validated before storing."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    language: Language
    format: QuestionFormat
    text: QuestionText
    option_a: ShortText | None = None
    option_b: ShortText | None = None
    facts: list[Fact] = Field(min_length=1, max_length=8)
    sources: list[Source] = Field(min_length=1, max_length=10)
    topic_area: str = Field(pattern=r"^[a-z][a-z_]*$")
    origin: QuestionOrigin
    #: Version of the prompt that drafted the question; `None` when written by hand.
    prompt_version: str | None = None
    #: Shared by the language versions (en, de) of the same question.
    group_id: uuid.UUID | None = None

    @property
    def single_source(self) -> bool:
        """True when all facts rest on one outlet (shown to the operator before approval)."""
        return len({source.outlet for source in self.sources}) < 2

    @model_validator(mode="after")
    def _check_consistency(self) -> Self:
        source_ids = [source.id for source in self.sources]
        if len(set(source_ids)) != len(source_ids):
            msg = "source ids must be unique"
            raise ValueError(msg)
        for fact in self.facts:
            unknown = set(fact.source_ids) - set(source_ids)
            if unknown:
                msg = f"fact references unknown source ids {sorted(unknown)}"
                raise ValueError(msg)
        has_options = self.option_a is not None or self.option_b is not None
        if self.format is QuestionFormat.TRADEOFF:
            if self.option_a is None or self.option_b is None:
                msg = "a tradeoff question needs option_a and option_b"
                raise ValueError(msg)
        elif has_options:
            msg = f"a {self.format} question must not have option_a/option_b"
            raise ValueError(msg)
        return self


class Question(QuestionContent):
    id: uuid.UUID
    status: QuestionStatus
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime
