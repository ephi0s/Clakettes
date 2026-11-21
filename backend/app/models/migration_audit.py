"""Audit trail for portability migrations between federated nodes."""

from sqlalchemy import Column, DateTime, Integer, String, Text
from datetime import datetime, timezone

from app.models.base import BaseModel


class MigrationAudit(BaseModel):
    __tablename__ = "migration_audits"

    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(String(50), nullable=False)
    source_domain = Column(String(255), nullable=True)
    target_domain = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
