"""Schemas for FestivalLocation — festival-location associations."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class FestivalLocationCreate(BaseModel):
    location_id: int


class FestivalLocationResponse(BaseModel):
    id: int
    festival_id: int
    location_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
