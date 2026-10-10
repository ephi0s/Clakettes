"""Schemas for LocationImage — gallery images for locations."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class LocationImageAdd(BaseModel):
    url: str


class LocationImageResponse(BaseModel):
    id: int
    location_id: int
    url: str
    source: str
    added_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
