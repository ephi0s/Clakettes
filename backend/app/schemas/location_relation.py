"""Schemas for LocationRelation — links between locations."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class LocationRelationCreate(BaseModel):
    related_location_id: int
    relation_type: str


class LocationRelationResponse(BaseModel):
    id: int
    location_id: int
    related_location_id: int
    relation_type: str
    suggested_by: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
