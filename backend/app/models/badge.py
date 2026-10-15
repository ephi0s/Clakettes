"""Badge models — merit insignias granted to user and festival profiles."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Badge(BaseModel):
    """A badge definition created by the platform admin team.

    ``scope`` is ``platform`` (granted by central admins) or ``festival``
    (granted by the festival in ``festival_id``, e.g. veteran participant,
    popular member, organizer role, or special prize). ``conditions`` holds a
    JSON descriptor such as ``{"type": "veteran", "min_festivals": 3}`` that is
    evaluated on assignment unless ``require_conditions`` is False.
    ``image_url`` points at the uploaded badge artwork (SVG preferred).
    """

    __tablename__ = "badges"

    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    scope = Column(String(20), default="platform")
    category = Column(String(30), nullable=True)
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True, index=True)
    conditions = Column(JSON, nullable=True)
    require_conditions = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    festival = relationship("Festival")
    assignments = relationship("BadgeAssignment", back_populates="badge", cascade="all, delete-orphan")


class BadgeAssignment(BaseModel):
    """A badge granted to a user profile or a festival profile."""

    __tablename__ = "badge_assignments"

    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False, index=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    target_festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True, index=True)
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    grant_festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True)
    reason = Column(Text, nullable=True)

    badge = relationship("Badge", back_populates="assignments")
