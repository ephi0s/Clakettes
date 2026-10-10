"""LocationRelation — proximity, tag, or suggested links between locations."""

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class LocationRelation(BaseModel):
    """Relates two locations by proximity, shared tags, or user suggestion."""

    __tablename__ = "location_relations"

    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    related_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    relation_type = Column(String(20), nullable=False)
    suggested_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    __table_args__ = (UniqueConstraint("location_id", "related_location_id", name="uq_location_relation"),)

    location = relationship("Location", foreign_keys=[location_id], back_populates="related_from")
    related_location = relationship("Location", foreign_keys=[related_location_id], back_populates="related_to")
    suggester = relationship("User", back_populates="suggested_location_relations")
