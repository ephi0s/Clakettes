"""Schemas for FestivalRulebook — bases of a festival."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from app.enums import FestivalRulebookCategory
from .common import PageBase

_VALID_CATEGORIES = {c.value for c in FestivalRulebookCategory}


class FestivalRulebookBase(BaseModel):
    title: str
    description: str | None = None
    category: str = FestivalRulebookCategory.OFFICIAL_SECTION.value
    event_id: int | None = None
    file_url: str | None = None
    external_url: str | None = None
    is_published: bool | None = True

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in _VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{v}'. Valid: {sorted(_VALID_CATEGORIES)}")
        return v


class FestivalRulebookCreate(FestivalRulebookBase):
    pass


class FestivalRulebookUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    event_id: int | None = None
    file_url: str | None = None
    external_url: str | None = None
    is_published: bool | None = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str | None) -> str | None:
        if v is not None and v not in _VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{v}'. Valid: {sorted(_VALID_CATEGORIES)}")
        return v


class FestivalRulebookResponse(FestivalRulebookBase):
    id: int
    festival_id: int
    created_by: int | None = None
    updated_by: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FestivalRulebooksPage(PageBase):
    items: list[FestivalRulebookResponse]
