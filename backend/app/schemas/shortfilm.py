from pydantic import BaseModel, ConfigDict, HttpUrl
from datetime import datetime
from .common import PageBase
from .shortfilm_location import ShortFilmLocationResponse


class ShortFilmBase(BaseModel):
    title: str
    description: str | None = None
    duration: int | None = None
    video_url: HttpUrl | None = None
    thumbnail_url: HttpUrl | None = None
    festival_id: int | None = None
    user_id: int
    is_public: bool | None = True
    tags: str | None = None


class ShortFilmCreate(ShortFilmBase):
    pass


class ShortFilmUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    duration: int | None = None
    video_url: HttpUrl | None = None
    thumbnail_url: HttpUrl | None = None
    festival_id: int | None = None
    is_public: bool | None = None
    tags: str | None = None


class ShortFilmResponse(ShortFilmBase):
    id: int
    created_at: datetime
    updated_at: datetime
    film_locations: list[ShortFilmLocationResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ShortFilmsPage(PageBase):
    items: list[ShortFilmResponse]
