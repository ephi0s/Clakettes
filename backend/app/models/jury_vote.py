"""JuryVote model — scoring by jury (Fase 5)."""

from sqlalchemy import Column, Integer, Float, String, ForeignKey
from app.models.base import BaseModel


class JuryVote(BaseModel):
    __tablename__ = "jury_votes"

    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=False, index=True)
    juror_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    shortfilm_id = Column(Integer, ForeignKey("shortfilms.id"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    comment = Column(String(500), nullable=True)
