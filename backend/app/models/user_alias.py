"""UserAlias model — users can have different display names/nicknames per context."""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.enums import AliasContext, AliasVisibility


class UserAlias(BaseModel):
    """Alternative display name for a user in a specific context.

    Users can have different names in different contexts:
    - Real name on public profile
    - Pseudonym for film credits
    - Nickname for chat
    - Festival-specific name for a particular festival
    """

    __tablename__ = "user_aliases"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    alias = Column(String(200), nullable=False)
    context = Column(
        SQLEnum(AliasContext, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=AliasContext.GLOBAL,
    )
    context_id = Column(Integer, nullable=True, index=True)  # Festival ID, ShortFilm ID, etc.
    is_primary = Column(Boolean, default=False)  # Primary alias for this context
    is_public = Column(Boolean, default=True)  # Visible to others
    show_awards = Column(Boolean, default=False)  # Whether awards linked to this context are shown
    profile_token = Column(String(64), nullable=True, unique=True, index=True)  # Unique URL token for partial profile
    visibility_scope = Column(
        SQLEnum(AliasVisibility, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=AliasVisibility.FESTIVAL_ONLY,
    )  # What festivals to show
    notes = Column(Text, nullable=True)  # Internal notes about why this alias exists

    # Relationships
    user = relationship("User", back_populates="aliases")

    def __repr__(self):
        ctx = f"{self.context.value}"
        if self.context_id:
            ctx += f":{self.context_id}"
        return f"<UserAlias(user_id={self.user_id}, alias='{self.alias}', context={ctx})>"
