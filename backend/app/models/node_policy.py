"""NodePolicy model — federation allowlist/blocklist per instance."""

from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel


class NodePolicy(BaseModel):
    __tablename__ = "node_policies"

    node_domain = Column(String(255), nullable=False, unique=True, index=True)
    allowed = Column(Boolean, nullable=False, default=True)
    consent_required = Column(Boolean, nullable=False, default=True)
    minimize_data = Column(Boolean, nullable=False, default=True)
    reason = Column(String(500), nullable=True)
