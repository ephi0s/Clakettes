"""RoleTransition — history of role changes (promotions, demotions, transfers, etc.)."""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class RoleTransition(BaseModel):
    """Tracks when a user's role changes: promotion, demotion, transfer, suspension, reactivation."""

    __tablename__ = "role_transitions"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    from_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    to_role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    from_festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True)
    to_festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True)
    transition_type = Column(
        String(30), nullable=False
    )  # promotion, demotion, transfer, suspension, reactivation, creation
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=True)
    transitioned_at = Column(DateTime, default=func.now())

    user = relationship("User", foreign_keys=[user_id], backref="role_transitions")
    from_role = relationship("Role", foreign_keys=[from_role_id], backref="transitions_from")
    to_role = relationship("Role", foreign_keys=[to_role_id], backref="transitions_to")
    from_festival = relationship("Festival", foreign_keys=[from_festival_id], backref="role_transitions_out")
    to_festival = relationship("Festival", foreign_keys=[to_festival_id], backref="role_transitions_in")
    changed_by_user = relationship("User", foreign_keys=[changed_by], backref="initiated_transitions")

    def __repr__(self):
        return (
            f"<RoleTransition(user={self.user_id}, {self.transition_type}: {self.from_role_id} -> {self.to_role_id})>"
        )
