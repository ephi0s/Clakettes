"""FestivalLocation — association between a festival and a location."""

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class FestivalLocation(BaseModel):
    """Links a festival to a location."""

    __tablename__ = "festival_locations"

    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("festival_id", "location_id", name="uq_festival_location"),)

    festival = relationship("Festival", back_populates="festival_locations")
    location = relationship("Location", back_populates="festival_locations")
