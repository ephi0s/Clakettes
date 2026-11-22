import threading
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.trusted_node import TrustedNode
from app.models.user import User
from app.routers.permissions import require_admin
from app.services.federation_metrics_service import FederationMetricsService
from app.services.node_peering_service import NodePeeringService

router = APIRouter(prefix="/api/federation/resilience", tags=["federation-resilience"])

metrics = FederationMetricsService()
peering = NodePeeringService()
_revocations = {}
_revocations_lock = threading.Lock()


class RevokeIn(BaseModel):
    node_domain: str
    reason: str | None = None


def _resolve_peer(request: Request, node: str | None, db: Session) -> TrustedNode:
    peer = getattr(request.state, "peer_node", None)
    domain = getattr(peer, "node_domain", None) if peer is not None else None
    if not domain:
        domain = node
    if not domain:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="node required")
    target = peering.get_by_domain(db, domain)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nodo no encontrado")
    if not target.allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Nodo revocado")
    return target


def _revocation_record(node_domain: str, reason: str | None, revoked_at, revoked_by) -> dict:
    return {
        "node_domain": node_domain,
        "reason": reason,
        "revoked_at": revoked_at.isoformat() if revoked_at else None,
        "revoked_by": revoked_by,
    }


def record_revocation(
    db: Session,
    node_domain: str,
    reason: str | None = None,
    revoked_by: str | None = None,
    revoked_at: datetime | None = None,
) -> TrustedNode | None:
    node = peering.get_by_domain(db, node_domain)
    if node is None:
        return None
    moment = revoked_at or datetime.now(timezone.utc)
    node.allowed = False
    node.revoked_at = moment
    node.revocation_reason = reason
    node.revoked_by = revoked_by
    db.commit()
    db.refresh(node)
    incident = _revocation_record(node_domain, reason, moment, revoked_by)
    with _revocations_lock:
        _revocations[node_domain] = incident
    return node


def clear_revocation(db: Session, node_domain: str) -> dict | None:
    with _revocations_lock:
        incident = _revocations.pop(node_domain, None)
    node = peering.get_by_domain(db, node_domain)
    if node is None:
        return incident
    if incident is None and not node.allowed:
        incident = _revocation_record(
            node_domain,
            node.revocation_reason,
            node.revoked_at or node.updated_at,
            node.revoked_by,
        )
    node.revoked_at = None
    node.revocation_reason = None
    node.revoked_by = None
    db.commit()
    return incident


@router.get("/health")
async def resilience_health(db: Session = Depends(get_db)):
    started = datetime.now(timezone.utc)
    try:
        db.execute(text("SELECT 1")).scalar()
        database = "up"
    except Exception:
        database = "down"
    node_count = db.query(func.count(TrustedNode.id)).scalar() or 0
    finished = datetime.now(timezone.utc)
    ok = database == "up"
    return {
        "status": "ok" if ok else "degraded",
        "alive": ok,
        "database": database,
        "node_count": node_count,
        "nodes": node_count,
        "peer_nodes": node_count,
        "server_time": finished.isoformat(),
        "latency_ms": round((finished - started).total_seconds() * 1000, 2),
        "version": "1.0.0",
    }


@router.get("/heartbeat")
async def resilience_heartbeat(request: Request, node: str | None = None, db: Session = Depends(get_db)):
    started = datetime.now(timezone.utc)
    target = _resolve_peer(request, node, db)
    now = datetime.now(timezone.utc)
    target.last_seen_at = now
    db.commit()
    db.refresh(target)
    finished = datetime.now(timezone.utc)
    metrics.record(
        target.node_domain,
        (finished - started).total_seconds() * 1000,
        True,
    )
    return {
        "node": target.node_domain,
        "alive": True,
        "server_time": now.isoformat(),
        "last_seen_at": target.last_seen_at.isoformat() if target.last_seen_at else None,
    }


@router.get("/metrics")
async def resilience_metrics():
    return metrics.snapshot()


@router.post("/keys/revoke")
async def resilience_revoke_key(
    body: RevokeIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user, db)
    started = datetime.now(timezone.utc)
    ok = peering.revoke(db, body.node_domain, reason=body.reason)
    if not ok:
        metrics.record(body.node_domain, (datetime.now(timezone.utc) - started).total_seconds() * 1000, False)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nodo no encontrado")
    node = record_revocation(db, body.node_domain, body.reason, str(current_user.id))
    revoked_at = node.revoked_at if node is not None else datetime.now(timezone.utc)
    metrics.record(
        body.node_domain,
        (datetime.now(timezone.utc) - started).total_seconds() * 1000,
        True,
    )
    return {
        "node_domain": body.node_domain,
        "revoked": True,
        "reason": body.reason,
        "revoked_at": revoked_at.isoformat(),
        "allowed": node.allowed if node is not None else False,
    }


@router.get("/keys/revoked")
async def resilience_revoked_keys(db: Session = Depends(get_db)):
    result = []
    for node in db.query(TrustedNode).filter(TrustedNode.allowed.is_(False)).all():
        result.append(
            _revocation_record(
                node.node_domain,
                node.revocation_reason,
                node.revoked_at or node.updated_at,
                node.revoked_by,
            )
        )
    return {"revoked": result, "count": len(result)}


@router.get("/incident-plan")
async def resilience_incident_plan():
    return {
        "version": "1.0.0",
        "plan_id": "federation-node-compromise",
        "title": "Plan de recuperación ante compromiso de nodo federado",
        "updated_at": "2026-11-20T00:00:00+00:00",
        "steps": [
            {
                "step": 1,
                "action": "Detectar y confirmar el compromiso mediante /health, /metrics y las sesiones de peering.",
            },
            {
                "step": 2,
                "action": "Revocar de inmediato el nodo afectado con POST /keys/revoke y motivo documentado.",
            },
            {
                "step": 3,
                "action": "Bloquear el dominio y la huella del certificado en la política de nodos.",
            },
            {
                "step": 4,
                "action": "Rotar credenciales y claves de federación; invalidar tokens emitidos por el nodo.",
            },
            {
                "step": 5,
                "action": "Auditar sesiones, exportaciones y mensajes intercambiados con el nodo.",
            },
            {
                "step": 6,
                "action": "Notificar a los nodos pares y propagar borrado de datos si aplica.",
            },
            {
                "step": 7,
                "action": "Restaurar el peering solo tras verificar identidad y nueva huella de certificado.",
            },
            {
                "step": 8,
                "action": "Registrar el incidente y actualizar este plan con lecciones aprendidas.",
            },
        ],
    }
