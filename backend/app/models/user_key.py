"""Model for storing E2EE public keys per user."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class UserKey(BaseModel):
    """Stores a user's X25519 public key for end-to-end encryption.

    Each user can have one active key pair. The private key never leaves
    the client device; only the public key is uploaded here so that other
    users can derive shared secrets.
    """

    __tablename__ = "user_keys"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    public_key_x25519 = Column(Text, nullable=False)  # base64-encoded 32-byte public key
    key_identifier = Column(String(64), nullable=False, unique=True)  # SHA-256 fingerprint
    is_active = Column(Integer, default=1)  # SQLite boolean
    rotated_at = Column(DateTime, nullable=True)

    user = relationship("User", foreign_keys=[user_id])

    @property
    def is_active_bool(self) -> bool:
        return bool(self.is_active)
