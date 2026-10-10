from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .common import PageBase


class AwardBase(BaseModel):
    festival_id: int
    event_id: int | None = None
    shortfilm_id: int | None = None
    user_id: int | None = None
    award_name: str
    award_category: str | None = None
    description: str | None = None
    position: int | None = None
    is_winner: bool = True
    prize_amount: float | None = None
    currency: str = "EUR"
    year: int | None = None
    is_public: bool = True


class AwardCreate(AwardBase):
    pass


class AwardUpdate(BaseModel):
    event_id: int | None = None
    shortfilm_id: int | None = None
    user_id: int | None = None
    award_name: str | None = None
    award_category: str | None = None
    description: str | None = None
    position: int | None = None
    is_winner: bool | None = None
    prize_amount: float | None = None
    currency: str | None = None
    year: int | None = None
    is_public: bool | None = None
    is_verified: bool | None = None


class AwardResponse(AwardBase):
    id: int
    is_verified: bool
    verified_by: int | None = None
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AwardPage(PageBase):
    items: list[AwardResponse]
