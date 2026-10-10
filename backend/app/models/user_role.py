"""UserRole model — links users to roles with festival scope and approval workflow."""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.enums import UserRoleStatus, UserRoleVisibility


class UserRole(BaseModel):
    """Assignment of a role to a user, optionally scoped to a festival.

    Supports:
    - Global roles (no festival_id): admin, producer, distributor, organism, sponsor
    - Festival-scoped roles: organizer, jury, programmer, technician, volunteer, etc.
    - Full workflow: proposed → invited → under_review → approved → active/expired
    - Time-limited assignments with expiry
    - Primary holder designation for shared roles
    - Per-role visibility control
    - Assignment tracking (who assigned, when, why)
    """

    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True, index=True)
    status = Column(
        SQLEnum(UserRoleStatus, values_callable=lambda x: [e.value for e in x]),
        default=UserRoleStatus.PENDING,
        nullable=False,
    )
    visibility = Column(
        SQLEnum(UserRoleVisibility, values_callable=lambda x: [e.value for e in x]),
        default=UserRoleVisibility.PUBLIC,
        nullable=False,
    )
    is_primary = Column(Boolean, default=False)  # Primary holder among multiple
    is_hidden = Column(Boolean, default=False)  # Legacy hidden flag (kept for compatibility)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=True)  # When the role becomes effective
    expires_at = Column(DateTime, nullable=True)  # Time-limited roles
    invitation_note = Column(Text, nullable=True)  # Reason for invitation/assignment
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    festival = relationship("Festival", back_populates="user_roles")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by], back_populates="assigned_roles")
    approved_by_user = relationship("User", foreign_keys=[approved_by], back_populates="approved_roles")

    def __repr__(self):
        scope = f"festival={self.festival_id}" if self.festival_id else "global"
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id}, {scope}, status={self.status.value})>"


class UserParticipantTag(BaseModel):
    """Assignment of a participant tag to a user, optionally scoped to a festival.

    A user (participant) can have multiple tags (director, actor, sound, etc.)
    Tags can be global (platform-wide) or festival-specific.
    """

    __tablename__ = "user_participant_tags"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("participant_tags.id"), nullable=False, index=True)
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True, index=True)
    is_primary = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="user_participant_tags")
    tag = relationship("ParticipantTag", back_populates="user_tags")
    festival = relationship("Festival", back_populates="user_participant_tags")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by], back_populates="assigned_participant_tags")

    def __repr__(self):
        scope = f"festival={self.festival_id}" if self.festival_id else "global"
        primary = " (primary)" if self.is_primary else ""
        return f"<UserParticipantTag(user_id={self.user_id}, tag_id={self.tag_id}, {scope}{primary})>"
