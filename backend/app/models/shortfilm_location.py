"""ShortFilmLocation — association between a short film and a location with temporal metadata."""

from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class ShortFilmLocation(BaseModel):
    """Links a short film to a location, optionally with time range and role."""

    __tablename__ = "shortfilm_locations"

    shortfilm_id = Column(Integer, ForeignKey("shortfilms.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    role = Column(String(20), nullable=False, default="primary")
    start_time = Column(Float, nullable=True)
    end_time = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    __table_args__ = (UniqueConstraint("shortfilm_id", "location_id", name="uq_shortfilm_location"),)

    shortfilm = relationship("ShortFilm", back_populates="film_locations")
    location = relationship("Location", back_populates="film_locations")
    creator = relationship("User", back_populates="film_location_links")
