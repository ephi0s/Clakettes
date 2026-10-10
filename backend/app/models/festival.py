"""Festival model — stores film festival information."""

from sqlalchemy import Column, String, Text, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Festival(BaseModel):
    """A film festival with geolocation, website, and active status.

    Relationships:
        shortfilms: Short films submitted to this festival.
        users: Users associated via the many-to-many ``user_festival`` table.
        festival_roles: Festival-specific role configurations.
        festival_participant_tags: Festival-specific participant tag configurations.
        user_roles: User-role assignments scoped to this festival.
        user_participant_tags: User-tag assignments scoped to this festival.
    """

    __tablename__ = "festivals"

    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True, index=True)
    location = Column(String(200), nullable=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    website = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    allow_alias_display = Column(Boolean, default=False)  # Users may show alias instead of real name
    show_in_calendar = Column(Boolean, default=True)  # Global admin controls agenda inclusion
    images = Column(JSON, nullable=True)  # List of image URLs

    shortfilms = relationship("ShortFilm", back_populates="festival")
    users = relationship("User", secondary="user_festival", back_populates="festivals")
    festival_roles = relationship("FestivalRole", back_populates="festival", cascade="all, delete-orphan")
    festival_participant_tags = relationship(
        "FestivalParticipantTag", back_populates="festival", cascade="all, delete-orphan"
    )
    user_roles = relationship("UserRole", back_populates="festival", cascade="all, delete-orphan")
    user_participant_tags = relationship("UserParticipantTag", back_populates="festival", cascade="all, delete-orphan")
    registration_forms = relationship("RegistrationForm", back_populates="festival", cascade="all, delete-orphan")
    registrations = relationship(
        "FestivalRegistration",
        foreign_keys="FestivalRegistration.festival_id",
        back_populates="festival",
        cascade="all, delete-orphan",
    )
    events = relationship("Event", back_populates="festival", cascade="all, delete-orphan")
    rulebooks = relationship("FestivalRulebook", back_populates="festival", cascade="all, delete-orphan")
    awards = relationship("Award", back_populates="festival", cascade="all, delete-orphan")
    festival_locations = relationship("FestivalLocation", back_populates="festival", cascade="all, delete-orphan")
