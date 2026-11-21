"""Identity redirect for users migrated between federated nodes."""

from sqlalchemy import Column, DateTime, String
from datetime import datetime, timezone

from app.models.base import BaseModel


class IdentityRedirect(BaseModel):
    __tablename__ = "identity_redirects"

    old_ref = Column(String(255), nullable=False, unique=True, index=True)
    new_ref = Column(String(255), nullable=False)
    target_domain = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
