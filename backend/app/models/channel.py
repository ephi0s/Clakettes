"""Channel and membership models for community rooms and private groups."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, func, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Channel(BaseModel):
    """A chat channel — either a public community or a private room (max 20 members).

    Types:
        - community: Open to all members of the festival / platform.
        - private:  Invite-only rooms capped at ``max_members`` (default 20).
    """

    __tablename__ = "channels"
    __table_args__ = (CheckConstraint("max_members IS NULL OR max_members > 0", name="ck_channel_max_members"),)

    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    channel_type = Column(String(20), nullable=False, default="community")  # community | private | broadcast
    max_members = Column(Integer, nullable=True, default=20)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True)

    creator = relationship("User", foreign_keys=[created_by])
    members = relationship("ChannelMember", back_populates="channel", cascade="all, delete-orphan")


class ChannelMember(BaseModel):
    """Membership and role within a channel."""

    __tablename__ = "channel_members"
    __table_args__ = (CheckConstraint("role IN ('admin', 'moderator', 'member')", name="ck_channel_member_role"),)

    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False, default="member")
    joined_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)

    channel = relationship("Channel", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
