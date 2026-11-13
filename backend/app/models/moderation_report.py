"""ModerationReport model — propagated reports between federated nodes."""

from sqlalchemy import Column, String, Text
from app.models.base import BaseModel


class ModerationReport(BaseModel):
    __tablename__ = "moderation_reports"

    reporter_node = Column(String(255), nullable=False, index=True)
    target_node = Column(String(255), nullable=False, index=True)
    target_user_ref = Column(String(255), nullable=True)
    reason = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
