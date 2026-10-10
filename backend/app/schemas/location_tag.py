"""Schemas for LocationTag — user-proposed tags for locations."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class LocationTagCreate(BaseModel):
    tag: str


class LocationTagResponse(BaseModel):
    id: int
    location_id: int
    tag: str
    proposed_by: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
