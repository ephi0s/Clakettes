"""Schemas para votación del jurado (Fase 5)."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VoteIn(BaseModel):
    festival_id: int
    shortfilm_id: int
    score: float = Field(..., ge=0, le=10)
    comment: str | None = Field(None, max_length=500)
    anonymous: bool = False


class VoteOut(BaseModel):
    id: int
    festival_id: int
    juror_id: int | None = None  # None si el voto es anónimo
    shortfilm_id: int
    score: float
    comment: str | None = None
    anonymous: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("created_at", mode="before")
    @classmethod
    def _format_created_at(cls, v):
        if v is None:
            return None
        return v.isoformat() if hasattr(v, "isoformat") else str(v)


class VoteAggregate(BaseModel):
    shortfilm_id: int
    average_score: float
    vote_count: int
    scores: list[float]


class FestivalAggregate(BaseModel):
    festival_id: int
    results: list[VoteAggregate]
