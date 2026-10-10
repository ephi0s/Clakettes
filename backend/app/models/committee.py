"""Committee model — sub-groups within festivals (Selection Committee, Technical Committee, Press Team, etc.)."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Committee(BaseModel):
    """A sub-group or committee within a festival (e.g., Selection Committee, Technical Committee)."""

    __tablename__ = "committees"

    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)  # Optional associated role
    is_active = Column(Boolean, default=True)
    max_members = Column(Integer, nullable=True)
    external_visible = Column(Boolean, default=False)  # Visible to public/external users

    festival = relationship("Festival", backref="committees")
    role = relationship("Role", backref="committees")
    members = relationship("CommitteeMember", back_populates="committee", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Committee(name='{self.name}', festival_id={self.festival_id})>"


class CommitteeMember(BaseModel):
    """A user's membership in a committee with their specific role."""

    __tablename__ = "committee_members"

    committee_id = Column(Integer, ForeignKey("committees.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_in_committee = Column(String(50), default="member")  # chair, vice_chair, member, secretary, advisor
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=func.now())
    notes = Column(Text, nullable=True)

    committee = relationship("Committee", back_populates="members")
    user = relationship("User", foreign_keys=[user_id], backref="committee_memberships")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by], backref="assigned_committee_members")

    def __repr__(self):
        return (
            f"<CommitteeMember(committee_id={self.committee_id}, "
            f"user_id={self.user_id}, role='{self.role_in_committee}')>"
        )
