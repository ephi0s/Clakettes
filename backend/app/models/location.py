"""Location model — named geographic places with metadata, images, and film associations."""

from sqlalchemy import Column, String, Text, Float, Boolean, JSON, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Location(BaseModel):
    """A named geographic place that can be used as a filming location.

    Relationships:
        added_by_user: The user who created this location.
        location_tags: Moderable tags proposed by users.
        film_locations: Short films shot at this location.
        location_images: Gallery images (uploaded or linked).
        related_from / related_to: Links to other locations.
    """

    __tablename__ = "locations"

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(300), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    tags = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    added_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    badge = Column(String(20), nullable=True)

    added_by_user = relationship("User", foreign_keys=[added_by], back_populates="added_locations")
    location_tags = relationship("LocationTag", back_populates="location", cascade="all, delete-orphan")
    film_locations = relationship("ShortFilmLocation", back_populates="location", cascade="all, delete-orphan")
    location_images = relationship("LocationImage", back_populates="location", cascade="all, delete-orphan")
    related_from = relationship(
        "LocationRelation",
        foreign_keys="LocationRelation.location_id",
        back_populates="location",
        cascade="all, delete-orphan",
    )
    related_to = relationship(
        "LocationRelation",
        foreign_keys="LocationRelation.related_location_id",
        back_populates="related_location",
        cascade="all, delete-orphan",
    )
    festival_locations = relationship("FestivalLocation", back_populates="location", cascade="all, delete-orphan")
