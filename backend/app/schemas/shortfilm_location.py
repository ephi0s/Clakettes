"""Schemas for ShortFilmLocation — film-location associations with temporal metadata."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ShortFilmLocationCreate(BaseModel):
    location_id: int
    role: str | None = "primary"
    start_time: float | None = None
    end_time: float | None = None
    notes: str | None = None


class ShortFilmLocationUpdate(BaseModel):
    role: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    notes: str | None = None


class ShortFilmLocationResponse(BaseModel):
    id: int
    shortfilm_id: int
    location_id: int
    role: str
    start_time: float | None = None
    end_time: float | None = None
    notes: str | None = None
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
