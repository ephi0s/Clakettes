from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
from datetime import datetime
from .common import PageBase


class FestivalBase(BaseModel):
    name: str
    description: str | None = None
    location: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    is_active: bool | None = True
    website: HttpUrl | None = None
    logo_url: HttpUrl | None = None
    allow_alias_display: bool | None = False
    show_in_calendar: bool | None = True
    images: list[str] = []

    @field_validator("images", mode="before")
    @classmethod
    def coerce_images(cls, v):
        return v or []


class FestivalCreate(FestivalBase):
    pass


class FestivalUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    location: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    is_active: bool | None = None
    website: HttpUrl | None = None
    logo_url: HttpUrl | None = None
    allow_alias_display: bool | None = None
    show_in_calendar: bool | None = None
    images: list[str] | None = None


class FestivalResponse(FestivalBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FestivalsPage(PageBase):
    items: list[FestivalResponse]
