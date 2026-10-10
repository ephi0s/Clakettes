from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .common import PageBase
from app.enums import ParticipantTagCategory


class ParticipantTagBase(BaseModel):
    name: str
    display_name: str
    description: str | None = None
    category: str = ParticipantTagCategory.OTHER.value
    is_global: bool = True
    is_active: bool = True
    sort_order: int = 0


class ParticipantTagCreate(ParticipantTagBase):
    pass


class ParticipantTagUpdate(BaseModel):
    display_name: str | None = None
    description: str | None = None
    category: str | None = None
    is_global: bool | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class ParticipantTagResponse(ParticipantTagBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FestivalParticipantTagBase(BaseModel):
    festival_id: int
    tag_id: int
    is_active: bool = True
    is_required: bool = False
    max_selections: int | None = None
    can_submit_films: bool = False
    max_film_submissions: int | None = None
    requires_approval: bool = False
    allowed_categories: str | None = None
    is_exclusive: bool = False


class FestivalParticipantTagCreate(FestivalParticipantTagBase):
    pass


class FestivalParticipantTagUpdate(BaseModel):
    is_active: bool | None = None
    is_required: bool | None = None
    max_selections: int | None = None
    can_submit_films: bool | None = None
    max_film_submissions: int | None = None
    requires_approval: bool | None = None
    allowed_categories: str | None = None
    is_exclusive: bool | None = None


class FestivalParticipantTagResponse(FestivalParticipantTagBase):
    id: int
    created_at: datetime
    updated_at: datetime
    tag: ParticipantTagResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class FestivalParticipantTagsPage(PageBase):
    items: list[FestivalParticipantTagResponse]


class ParticipantTagsPage(PageBase):
    items: list[ParticipantTagResponse]
