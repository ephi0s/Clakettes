"""UserFollow model — tracks which users follow other users."""

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class UserFollow(BaseModel):
    __tablename__ = "user_follows"

    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    followed_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("follower_id", "followed_id", name="uq_user_follow"),)

    follower = relationship("User", foreign_keys=[follower_id])
    followed = relationship("User", foreign_keys=[followed_id])
