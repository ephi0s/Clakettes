"""ParticipantTag model — tags for participant roles/skills (director, actor, sound, etc.)."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.enums import ParticipantTagCategory


class ParticipantTag(BaseModel):
    """Tag representing a participant's role/skill in film production."""

    __tablename__ = "participant_tags"

    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default=ParticipantTagCategory.OTHER.value)
    is_global = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    user_tags = relationship("UserParticipantTag", back_populates="tag")
    festival_tags = relationship("FestivalParticipantTag", back_populates="tag")

    def __repr__(self):
        return f"<ParticipantTag(name='{self.name}', category='{self.category}')>"


class FestivalParticipantTag(BaseModel):
    """Festival-specific participant tag configuration with restrictions."""

    __tablename__ = "festival_participant_tags"

    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("participant_tags.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_required = Column(Boolean, default=False)
    max_selections = Column(Integer, nullable=True)
    can_submit_films = Column(Boolean, default=False)
    max_film_submissions = Column(Integer, nullable=True)
    requires_approval = Column(Boolean, default=False)
    allowed_categories = Column(Text, nullable=True)
    is_exclusive = Column(Boolean, default=False)

    festival = relationship("Festival", back_populates="festival_participant_tags")
    tag = relationship("ParticipantTag", back_populates="festival_tags")

    def __repr__(self):
        return f"<FestivalParticipantTag(festival_id={self.festival_id}, tag_id={self.tag_id})>"
