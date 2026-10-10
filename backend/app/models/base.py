"""Abstract base model providing id, created_at, and updated_at fields."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    """Abstract base for all domain models.

    Every table inheriting from this will include:
        id: Auto-increment integer primary key.
        created_at: Timestamp set on creation.
        updated_at: Timestamp refreshed on every update.
    """

    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
