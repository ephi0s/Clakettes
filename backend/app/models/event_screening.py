from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.enums import ScreeningStatus


class EventScreening(BaseModel):
    __tablename__ = "event_screenings"

    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    shortfilm_id = Column(Integer, ForeignKey("shortfilms.id", ondelete="CASCADE"), nullable=False, index=True)
    sort_order = Column(Integer, default=0)
    status = Column(String(50), nullable=False, default=ScreeningStatus.PENDING.value)
    status_reason = Column(Text, nullable=True)
    jury_notes = Column(Text, nullable=True)
    minutes = Column(Text, nullable=True)
    annotation = Column(String(50), nullable=True)
    annotated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    annotated_at = Column(DateTime, nullable=True)

    event = relationship("Event", back_populates="screenings")
    shortfilm = relationship("ShortFilm")
    annotator = relationship("User", foreign_keys=[annotated_by])

    @property
    def is_disqualified(self) -> bool:
        return self.status == ScreeningStatus.DISQUALIFIED.value
