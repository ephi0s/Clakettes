"""ShortFilm model — short film entries submitted to festivals."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class ShortFilm(BaseModel):
    """A short film uploaded by a user, optionally linked to a festival.

    Relationships:
        festival: The festival this film was submitted to (optional).
        user: The user who uploaded the film.
    """

    __tablename__ = "shortfilms"

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)
    video_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=True)
    tags = Column(Text, nullable=True)

    festival = relationship("Festival", back_populates="shortfilms")
    user = relationship("User", back_populates="shortfilms")
    awards = relationship("Award", back_populates="shortfilm")
    film_locations = relationship("ShortFilmLocation", back_populates="shortfilm", cascade="all, delete-orphan")
