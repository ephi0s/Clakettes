"""Notification model — in-app notifications for profile changes and system events."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Notification(BaseModel):
    """An in-app notification sent to a user.

    Created automatically when an admin or organizer modifies another
    user's profile. Supports marking as read and deletion.
    """

    __tablename__ = "notifications"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False, default="profile_update")
    is_read = Column(Boolean, default=False)
    related_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", foreign_keys=[user_id], backref="notifications")
    related_user = relationship("User", foreign_keys=[related_user_id])
