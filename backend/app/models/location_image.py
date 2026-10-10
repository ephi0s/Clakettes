"""LocationImage model — images attached to locations."""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class LocationImage(BaseModel):
    """An image (uploaded or linked) for a specific location."""

    __tablename__ = "location_images"

    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    url = Column(String(500), nullable=False)
    source = Column(String(20), nullable=False, default="upload")
    added_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    location = relationship("Location", back_populates="location_images")
    adder = relationship("User", back_populates="added_location_images")
