"""Service for federation node allowlist/blocklist policies."""

from sqlalchemy.orm import Session
from app.models.node_policy import NodePolicy
from .base_service import BaseService


class NodePolicyService(BaseService[NodePolicy, NodePolicy, NodePolicy]):
    def __init__(self):
        super().__init__(NodePolicy)

    def set_policy(self, db: Session, node_domain: str, allowed: bool, reason: str | None = None) -> NodePolicy:
        existing = db.query(NodePolicy).filter(NodePolicy.node_domain == node_domain).first()
        if existing:
            existing.allowed = allowed
            existing.reason = reason
            db.commit()
            db.refresh(existing)
            return existing
        obj = NodePolicy(node_domain=node_domain, allowed=allowed, reason=reason)
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
