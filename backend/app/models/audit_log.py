"""AuditLog model — append-only record of sensitive actions (RGPD art. 5.2).

Rows are never deleted by user erasure so accountability survives the
right to be forgotten; they reference anonymized user ids afterwards.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.models.base import BaseModel


class AuditLog(BaseModel):
    """Who did what, to whom, when and from where.

    Actions (dot-namespaced): ``user.erase``, ``user.export``,
    ``user.role.assign``, ``user.role.update``, ``user.role.remove``,
    ``user.tag.assign``, ``user.tag.remove``, ``dav.token.issue``,
    ``dav.token.revoke``.
    """

    __tablename__ = "audit_logs"

    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    detail = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
