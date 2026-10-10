"""FestivalRulebook model — bases of a festival (official section, contests, activities)."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.enums import FestivalRulebookCategory
from app.models.base import BaseModel


class FestivalRulebook(BaseModel):
    """Bases/conditions published by a festival.

    Each rulebook belongs to a festival and optionally to one of its
    events (contest or activity). The document itself is offered either
    as an uploaded file (usually PDF, stored in ``file_url``) or as an
    external URL (``external_url``). At least one of the two should be
    set, but both may coexist (external mirror of the uploaded file).
    """

    __tablename__ = "festival_rulebooks"

    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default=FestivalRulebookCategory.OFFICIAL_SECTION.value)
    file_url = Column(String(500), nullable=True)
    external_url = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    festival = relationship("Festival", back_populates="rulebooks")
    event = relationship("Event", back_populates="rulebooks")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
