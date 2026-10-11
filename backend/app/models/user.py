"""User model — platform user profile with authentication and geolocation."""

from sqlalchemy import Column, String, Text, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    """A platform user with login credentials, profile info, and visibility settings.

    Relationships:
        shortfilms: Short films uploaded by this user.
        festivals: Festivals the user participates in (many-to-many).
        user_roles: Role assignments (global and festival-scoped).
        user_participant_tags: Participant tag assignments (global and festival-scoped).
        assigned_roles: Roles this user has assigned to others.
        approved_roles: Roles this user has approved.
        assigned_participant_tags: Tags this user has assigned to others.
        aliases: Alternative display names per context.
    """

    __tablename__ = "users"

    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True, index=True)
    role = Column(String(50), nullable=True)  # Legacy field, kept for backwards compatibility
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    is_public_email = Column(Boolean, default=False)
    is_public_bio = Column(Boolean, default=False)
    is_public_location = Column(Boolean, default=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # RGPD art. 7 — registro del consentimiento de la política de privacidad.
    # NULL en cuentas anteriores = consentimiento no registrado.
    privacy_policy_version = Column(String(20), nullable=True)
    privacy_accepted_at = Column(DateTime, nullable=True)

    # SHA-256 of the CalDAV access token. NULL means no token has been issued.
    # The plaintext is shown once at generation time and never stored, so a
    # database leak cannot be replayed as a calendar credential.
    dav_token_hash = Column(String(64), nullable=True, unique=True, index=True)
    # RGPD art. 32 — los tokens DAV caducan (ver DAV_TOKEN_EXPIRE_DAYS).
    dav_token_expires_at = Column(DateTime, nullable=True)

    shortfilms = relationship("ShortFilm", back_populates="user")
    festivals = relationship("Festival", secondary="user_festival", back_populates="users")
    user_roles = relationship(
        "UserRole", foreign_keys="UserRole.user_id", back_populates="user", cascade="all, delete-orphan"
    )
    user_participant_tags = relationship(
        "UserParticipantTag",
        foreign_keys="UserParticipantTag.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    assigned_roles = relationship("UserRole", foreign_keys="UserRole.assigned_by", back_populates="assigned_by_user")
    approved_roles = relationship("UserRole", foreign_keys="UserRole.approved_by", back_populates="approved_by_user")
    assigned_participant_tags = relationship(
        "UserParticipantTag", foreign_keys="UserParticipantTag.assigned_by", back_populates="assigned_by_user"
    )
    aliases = relationship("UserAlias", back_populates="user", cascade="all, delete-orphan")
    festival_registrations = relationship(
        "FestivalRegistration",
        foreign_keys="FestivalRegistration.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    assigned_registrations = relationship(
        "FestivalRegistration", foreign_keys="FestivalRegistration.assigned_by", back_populates="assigned_by_user"
    )
    approved_registrations = relationship(
        "FestivalRegistration", foreign_keys="FestivalRegistration.approved_by", back_populates="approved_by_user"
    )
    created_events = relationship("Event", foreign_keys="Event.created_by", back_populates="creator")
    event_attendances = relationship("EventAttendee", foreign_keys="EventAttendee.user_id", back_populates="user")
    event_invitations = relationship("EventAttendee", foreign_keys="EventAttendee.invited_by", back_populates="inviter")
    event_reservations = relationship(
        "EventReservation", foreign_keys="EventReservation.user_id", back_populates="user"
    )
    awards = relationship("Award", foreign_keys="Award.user_id", back_populates="user")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    added_locations = relationship("Location", foreign_keys="Location.added_by", back_populates="added_by_user")
    proposed_location_tags = relationship("LocationTag", back_populates="proposer")
    film_location_links = relationship("ShortFilmLocation", back_populates="creator")
    added_location_images = relationship("LocationImage", back_populates="adder")
    suggested_location_relations = relationship("LocationRelation", back_populates="suggester")
