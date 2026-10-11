"""Audit log service — append-only record of sensitive actions (RGPD art. 5.2)."""

import json

from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate, AuditLogUpdate
from .base_service import BaseService


class AuditService(BaseService[AuditLog, AuditLogCreate, AuditLogUpdate]):
    def __init__(self):
        super().__init__(AuditLog)

    def log(
        self,
        db: Session,
        action: str,
        actor_user_id: int | None = None,
        target_user_id: int | None = None,
        detail: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_user_id=target_user_id,
            detail=json.dumps(detail, sort_keys=True) if detail else None,
            ip_address=ip_address,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    def list_paginated(
        self,
        db: Session,
        page: int = 1,
        size: int = 20,
        action: str | None = None,
        actor_user_id: int | None = None,
    ) -> dict:
        query = db.query(AuditLog).order_by(AuditLog.id.desc())
        if action:
            query = query.filter(AuditLog.action == action)
        if actor_user_id:
            query = query.filter(AuditLog.actor_user_id == actor_user_id)
        return self.paginate(query, page, size)
