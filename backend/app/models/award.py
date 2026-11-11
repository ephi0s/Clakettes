"""Award model — tracks prizes and awards won by users/films in festivals."""

import json

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Award(BaseModel):
    """An award or prize given in a festival to a film or person.

    Awards can be:
    - Film awards: Best Short Film, Best Director, Best Actor, etc.
    - Person awards: Honorary mention, special jury prize, etc.
    - Tracked per festival and optionally per event.

    Visibility can be controlled by the recipient (for person awards)
    and by the festival (for official records).
    """

    __tablename__ = "awards"

    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)  # Awarded during a specific event
    shortfilm_id = Column(Integer, ForeignKey("shortfilms.id"), nullable=True)  # Awarded to a film
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Awarded to a person
    award_name = Column(String(200), nullable=False)  # e.g., "Best Short Film", "Best Director"
    award_category = Column(String(100), nullable=True)  # e.g., "Official Competition", "Student Films"
    description = Column(Text, nullable=True)
    position = Column(Integer, nullable=True)  # 1st, 2nd, 3rd place
    is_winner = Column(Boolean, default=True)
    prize_amount = Column(Float, nullable=True)
    currency = Column(String(3), default="EUR")
    year = Column(Integer, nullable=True)
    is_public = Column(Boolean, default=True)  # Visible on public profiles
    is_verified = Column(Boolean, default=False)  # Confirmed by festival organizers
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    eligibility_criteria = Column(Text, nullable=True)  # JSON list of required participant tags
    recipient_verified = Column(Boolean, default=False, nullable=False)
    recipient_verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    recipient_verified_at = Column(DateTime, nullable=True)
    recipient_verification_notes = Column(Text, nullable=True)

    festival = relationship("Festival", back_populates="awards")
    event = relationship("Event", back_populates="awards")
    shortfilm = relationship("ShortFilm", back_populates="awards")
    user = relationship("User", foreign_keys=[user_id], back_populates="awards")
    verifier = relationship("User", foreign_keys=[verified_by])
    recipient_verifier = relationship("User", foreign_keys=[recipient_verified_by])
    creator = relationship("User", foreign_keys=[created_by])

    @property
    def eligibility_tags(self) -> list[str]:
        raw = self.eligibility_criteria
        if not raw:
            return []
        try:
            data = json.loads(raw)
        except (TypeError, ValueError):
            return [part.strip() for part in raw.split(",") if part.strip()]
        if isinstance(data, list):
            return [str(item) for item in data]
        return [str(data)]

    @eligibility_tags.setter
    def eligibility_tags(self, value) -> None:
        self.eligibility_criteria = json.dumps(list(value or []), ensure_ascii=False)

    def __repr__(self):
        return f"<Award(id={self.id}, name='{self.award_name}', festival_id={self.festival_id})>"
