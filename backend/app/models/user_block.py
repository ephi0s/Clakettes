"""UserBlock model — tracks users blocked by a user (RGPD / safety)."""

from sqlalchemy import Column, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class UserBlock(BaseModel):
    __tablename__ = "user_blocks"

    blocker_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    blocked_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reason = Column(Text, nullable=True)

    __table_args__ = (UniqueConstraint("blocker_id", "blocked_id", name="uq_user_block"),)

    blocker = relationship("User", foreign_keys=[blocker_id])
    blocked = relationship("User", foreign_keys=[blocked_id])
