"""RoleDelegation — temporary delegation of role authority from one user to another."""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.enums import DelegationStatus


class RoleDelegation(BaseModel):
    """Temporary delegation of a role's authority from delegator to delegate.

    The delegate can act on behalf of the delegator for the specified role.
    """

    __tablename__ = "role_delegations"

    delegator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    delegate_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True)
    status = Column(String(20), default=DelegationStatus.ACTIVE.value, nullable=False)
    starts_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    reason = Column(Text, nullable=True)
    scope_limitations = Column(Text, nullable=True)  # e.g., "read-only", "except financial decisions"
    revoked_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    revoked_reason = Column(Text, nullable=True)

    delegator = relationship("User", foreign_keys=[delegator_id], backref="delegations_made")
    delegate = relationship("User", foreign_keys=[delegate_id], backref="delegations_received")
    role = relationship("Role", backref="delegations")
    festival = relationship("Festival", backref="role_delegations")
    revoker = relationship("User", foreign_keys=[revoked_by], backref="revoked_delegations")

    def __repr__(self):
        return f"<RoleDelegation(delegator={self.delegator_id} -> {self.delegate_id}, role={self.role_id})>"
