"""Service for federation node allowlist/blocklist policies."""

from sqlalchemy.orm import Session
from app.models.node_policy import NodePolicy
from .base_service import BaseService


class NodePolicyService(BaseService[NodePolicy, NodePolicy, NodePolicy]):
    def __init__(self):
        super().__init__(NodePolicy)

    def set_policy(
        self,
        db: Session,
        node_domain: str,
        allowed: bool,
        consent_required: bool = True,
        minimize_data: bool = True,
        reason: str | None = None,
    ) -> NodePolicy:
        existing = db.query(NodePolicy).filter(NodePolicy.node_domain == node_domain).first()
        if existing:
            existing.allowed = allowed
            existing.consent_required = consent_required
            existing.minimize_data = minimize_data
            existing.reason = reason
            db.commit()
            db.refresh(existing)
            return existing
        obj = NodePolicy(
            node_domain=node_domain,
            allowed=allowed,
            consent_required=consent_required,
            minimize_data=minimize_data,
            reason=reason,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def is_allowed(self, db: Session, node_domain: str) -> bool:
        policy = db.query(NodePolicy).filter(NodePolicy.node_domain == node_domain).first()
        if policy is None:
            return True
        return bool(policy.allowed)

    def list_policies(self, db: Session):
        return db.query(NodePolicy).order_by(NodePolicy.node_domain).all()
