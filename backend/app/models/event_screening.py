from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class EventScreening(BaseModel):
    __tablename__ = "event_screenings"

    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    shortfilm_id = Column(Integer, ForeignKey("shortfilms.id", ondelete="CASCADE"), nullable=False, index=True)
    sort_order = Column(Integer, default=0)

    event = relationship("Event", back_populates="screenings")
    shortfilm = relationship("ShortFilm")
