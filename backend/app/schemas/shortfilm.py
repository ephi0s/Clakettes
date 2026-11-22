from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from app.enums import ShortFilmContestType
from .common import MediaUrl, PageBase
from .shortfilm_location import ShortFilmLocationResponse

_VALID_CONTEST_TYPES = {t.value for t in ShortFilmContestType}


class ShortFilmBase(BaseModel):
    title: str
    description: str | None = None
    duration: int | None = None
    video_url: MediaUrl | None = None
    thumbnail_url: MediaUrl | None = None
    festival_id: int
    contest_type: str = ShortFilmContestType.OFFICIAL_SECTION.value
    user_id: int
    is_public: bool | None = True
    tags: str | None = None

    @field_validator("contest_type")
    @classmethod
    def validate_contest_type(cls, v: str) -> str:
        if v not in _VALID_CONTEST_TYPES:
            raise ValueError(f"Invalid contest type '{v}'. Valid: {sorted(_VALID_CONTEST_TYPES)}")
        return v


class ShortFilmCreate(ShortFilmBase):
    pass


class FestivalShortFilmCreate(BaseModel):
    title: str
    description: str | None = None
    duration: int | None = None
    video_url: MediaUrl | None = None
    thumbnail_url: MediaUrl | None = None
    contest_type: str = ShortFilmContestType.OFFICIAL_SECTION.value
    is_public: bool | None = True
    tags: str | None = None

    @field_validator("contest_type")
    @classmethod
    def validate_contest_type(cls, v: str) -> str:
        if v not in _VALID_CONTEST_TYPES:
            raise ValueError(f"Invalid contest type '{v}'. Valid: {sorted(_VALID_CONTEST_TYPES)}")
        return v


class ShortFilmUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    duration: int | None = None
    video_url: MediaUrl | None = None
    thumbnail_url: MediaUrl | None = None
    contest_type: str | None = None
    is_public: bool | None = None
    tags: str | None = None

    @field_validator("contest_type")
    @classmethod
    def validate_contest_type(cls, v: str | None) -> str | None:
        if v is not None and v not in _VALID_CONTEST_TYPES:
            raise ValueError(f"Invalid contest type '{v}'. Valid: {sorted(_VALID_CONTEST_TYPES)}")
        return v


class ShortFilmResponse(ShortFilmBase):
    id: int
    created_at: datetime
    updated_at: datetime
    film_locations: list[ShortFilmLocationResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ShortFilmSummary(BaseModel):
    id: int
    title: str
    thumbnail_url: MediaUrl | None = None
    contest_type: str
    duration: int | None = None
    is_public: bool | None = None

    model_config = ConfigDict(from_attributes=True)


class ShortFilmsPage(PageBase):
    items: list[ShortFilmResponse]
