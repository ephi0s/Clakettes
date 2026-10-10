from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from .common import PageBase
from .location_tag import LocationTagResponse
from .location_image import LocationImageResponse
from .shortfilm_location import ShortFilmLocationResponse


class LocationBase(BaseModel):
    name: str
    description: str | None = None
    address: str | None = None
    latitude: float
    longitude: float
    tags: list[str] = []
    images: list[str] = []
    is_active: bool | None = True
    badge: str | None = None

    @field_validator("tags", "images", mode="before")
    @classmethod
    def coerce_lists(cls, v):
        return v or []


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    tags: list[str] | None = None
    images: list[str] | None = None
    is_active: bool | None = None
    badge: str | None = None


class LocationResponse(LocationBase):
    id: int
    added_by: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LocationDetailResponse(LocationResponse):
    location_tags: list[LocationTagResponse] = []
    location_images: list[LocationImageResponse] = []
    related_location_ids: list[int] = []
    film_locations: list[ShortFilmLocationResponse] = []


class LocationsPage(PageBase):
    items: list[LocationResponse]
