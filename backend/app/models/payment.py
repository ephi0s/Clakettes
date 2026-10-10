from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Payment(BaseModel):
    __tablename__ = "payments"

    registration_id = Column(
        Integer, ForeignKey("festival_registrations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    event_id = Column(Integer, ForeignKey("events.id", ondelete="SET NULL"), nullable=True, index=True)
    amount = Column(Float, nullable=False, default=0.0)
    currency = Column(String(3), default="EUR", nullable=False)
    provider = Column(String(30), default="mock", nullable=False, index=True)
    status = Column(String(20), default="pending", nullable=False, index=True)
    provider_ref = Column(String(100), nullable=True, unique=True, index=True)
    checkout_url = Column(String(500), nullable=True)

    registration = relationship("FestivalRegistration")
    event = relationship("Event")
