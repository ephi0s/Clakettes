"""LocationTag model — user-proposed tags for locations."""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class LocationTag(BaseModel):
    """A tag proposed by a user for a specific location."""

    __tablename__ = "location_tags"

    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    tag = Column(String(50), nullable=False)
    proposed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, default="approved")

    location = relationship("Location", back_populates="location_tags")
    proposer = relationship("User", back_populates="proposed_location_tags")
