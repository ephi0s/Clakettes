"""Many-to-many association table linking users to festivals."""

from sqlalchemy import Column, Integer, ForeignKey, Table, DateTime, String, func
from app.models.base import Base

user_festival = Table(
    "user_festival",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("festival_id", Integer, ForeignKey("festivals.id"), primary_key=True),
    Column("role", String(50), nullable=True),
    Column("joined_at", DateTime, default=func.now()),
)
