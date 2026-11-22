from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from .common import MediaUrl, PageBase
from .shortfilm import ShortFilmSummary


class FestivalBase(BaseModel):
    name: str
    description: str | None = None
    location: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    is_active: bool | None = True
    website: MediaUrl | None = None
    logo_url: MediaUrl | None = None
    banner_url: MediaUrl | None = None
    tagline: str | None = Field(None, max_length=200)
    social_links: dict[str, str] | None = None
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
    website: MediaUrl | None = None
    logo_url: MediaUrl | None = None
    banner_url: MediaUrl | None = None
    tagline: str | None = Field(None, max_length=200)
    social_links: dict[str, str] | None = None
    allow_alias_display: bool | None = None
    show_in_calendar: bool | None = None
    images: list[str] | None = None


class FestivalResponse(FestivalBase):
    id: int
    created_at: datetime
    updated_at: datetime
    shortfilm_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class FestivalDetailResponse(FestivalResponse):
    shortfilms: list[ShortFilmSummary] = []


class FestivalsPage(PageBase):
    items: list[FestivalResponse]
