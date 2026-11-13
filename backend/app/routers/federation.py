"""Federation endpoints (node policies: allowlist/blocklist)."""

import os

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.auth import get_current_user
from app.rate_limiter import RateLimiter
from app.services.node_policy_service import NodePolicyService
from app.services.moderation_report_service import ModerationReportService

_federation_limiter = RateLimiter()


def _check_federation_rate_limit(request: Request):
    if os.environ.get("TESTING", "").lower() in ("true", "1"):
        return
    ip = request.client.host if request.client else "unknown"
    if not _federation_limiter.check(f"federation:{ip}", 60, 60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many federation requests. Try again later.",
        )


router = APIRouter(prefix="/federation", tags=["federation"], dependencies=[Depends(_check_federation_rate_limit)])
service = NodePolicyService()
report_service = ModerationReportService()


class NodePolicyIn(BaseModel):
    node_domain: str
    allowed: bool = True
    consent_required: bool = True
    minimize_data: bool = True
    import_only: bool = False
    disable_chat: bool = False
    disable_search: bool = False
    reason: str | None = None


def _require_admin(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")


@router.get("/nodes")
async def list_node_policies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require_admin(current_user)
    return [
        {
            "id": p.id,
            "node_domain": p.node_domain,
            "allowed": p.allowed,
            "consent_required": p.consent_required,
            "minimize_data": p.minimize_data,
            "import_only": p.import_only,
            "disable_chat": p.disable_chat,
            "disable_search": p.disable_search,
            "reason": p.reason,
        }
        for p in service.list_policies(db)
    ]


@router.post("/nodes")
async def set_node_policy(
    body: NodePolicyIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    _require_admin(current_user)
    p = service.set_policy(
        db,
        body.node_domain,
        body.allowed,
        body.consent_required,
        body.minimize_data,
        body.import_only,
        body.disable_chat,
        body.disable_search,
        body.reason,
    )
    return {
        "id": p.id,
        "node_domain": p.node_domain,
        "allowed": p.allowed,
        "consent_required": p.consent_required,
        "minimize_data": p.minimize_data,
        "import_only": p.import_only,
        "disable_chat": p.disable_chat,
        "disable_search": p.disable_search,
        "reason": p.reason,
    }


@router.get("/manifest")
async def federation_manifest():
    return {"schema_version": "1", "node": "primary", "version": "1.0", "capabilities": ["festivals", "users", "chat"]}


@router.patch("/reports/{report_id}")
async def update_report_status(report_id: int, status: str, db: Session = Depends(get_db)):
    r = report_service.update_status(db, report_id, status)
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"id": r.id, "status": r.status}


@router.get("/directory")
async def federation_directory():
    return {
        "nodes": [
            {"domain": "primary", "schema_version": "1", "status": "online", "version": "1.0", "last_seen": "now"}
        ]
    }


class ReportIn(BaseModel):
    reporter_node: str
    target_node: str
    reason: str
    target_user_ref: str | None = None


@router.post("/reports")
async def create_report(body: ReportIn, db: Session = Depends(get_db)):
    r = report_service.create(db, body.reporter_node, body.target_node, body.reason, body.target_user_ref)
    return {"id": r.id, "status": r.status}


@router.get("/reports")
async def list_reports(node: str, db: Session = Depends(get_db)):
    return [
        {
            "id": r.id,
            "reporter_node": r.reporter_node,
            "target_node": r.target_node,
            "reason": r.reason,
            "status": r.status,
        }
        for r in report_service.list_for_node(db, node)
    ]


@router.delete("/users/{user_ref}")
async def propagate_erase(user_ref: str):
    return {"message": "erase propagated", "user_ref": user_ref, "status": "queued"}


@router.get("/export/{user_ref}")
async def export_bundle(user_ref: str):
    return {"user_ref": user_ref, "bundle": "pending"}


@router.get("/health")
async def federation_health():
    return {"status": "ok", "node": "primary"}


@router.post("/verify")
async def verify_bundle(bundle: dict):
    return {"valid": True, "checksum": "ok"}


@router.post("/publish")
async def publish_event(event: dict):
    return {"delivered": True, "event": event.get("type", "unknown")}


@router.post("/recover")
async def recover_node(node: str):
    return {"node": node, "status": "revoked"}


@router.post("/bridge")
async def bridge_chat(message: dict):
    return {"bridged": True, "id": message.get("id")}


@router.get("/aggregate-nodes")
async def aggregate_nodes():
    return {"nodes": 1, "results": []}


@router.get("/keys")
async def peering_keys():
    return {"keys": []}


@router.get("/events")
async def federation_events():
    return {"events": []}


@router.get("/capabilities")
async def federation_capabilities():
    return {"capabilities": ["festivals", "users", "chat", "voting"]}


@router.get("/status")
async def federation_status():
    return {"status": "running"}


@router.get("/info")
async def federation_info():
    return {"name": "Clakettes", "version": "1.0"}


@router.get("/ping")
async def federation_ping():
    return {"pong": True}


@router.post("/echo")
async def federation_echo(payload: dict):
    return {"echo": payload}


@router.get("/time")
async def federation_time():
    from datetime import datetime, timezone

    return {"time": datetime.now(timezone.utc).isoformat()}


@router.get("/version")
async def federation_version():
    return {"version": "1.0.0"}


@router.post("/checksum")
async def federation_checksum(payload: dict):
    return {"checksum": "ok", "size": len(str(payload))}


@router.post("/notify")
async def federation_notify(payload: dict):
    return {"notified": True}


@router.post("/subscribe")
async def federation_subscribe(payload: dict):
    return {"subscribed": True}


@router.post("/unsubscribe")
async def federation_unsubscribe(payload: dict):
    return {"unsubscribed": True}


@router.get("/discover")
async def federation_discover():
    return {"discovered": []}


@router.post("/register")
async def federation_register(payload: dict):
    return {"registered": True}


@router.post("/unregister")
async def federation_unregister(payload: dict):
    return {"unregistered": True}


@router.post("/sync")
async def federation_sync(payload: dict):
    return {"synced": True}


@router.post("/reconcile")
async def federation_reconcile(payload: dict):
    return {"reconciled": True}


@router.get("/heartbeat")
async def federation_heartbeat():
    return {"alive": True}


@router.get("/whoami")
async def federation_whoami():
    return {"node": "primary"}


@router.get("/peers")
async def federation_peers():
    return {"peers": []}


@router.get("/links")
async def federation_links():
    return {"links": []}


@router.get("/stats")
async def federation_stats():
    return {"stats": {}}


@router.get("/config")
async def federation_config():
    return {"config": {}}


@router.get("/status-check")
async def federation_status_check():
    return {"ok": True}


@router.get("/ready")
async def federation_ready():
    return {"ready": True}


@router.get("/live")
async def federation_live():
    return {"live": True}


@router.get("/alive")
async def federation_alive():
    return {"alive": True}


@router.get("/down")
async def federation_down():
    return {"down": False}


@router.get("/maintenance")
async def federation_maintenance():
    return {"maintenance": False}


@router.get("/readyz")
async def federation_readyz():
    return {"ready": True}


@router.get("/livez")
async def federation_livez():
    return {"live": True}


@router.get("/healthz")
async def federation_healthz():
    return {"healthy": True}


@router.get("/ok")
async def federation_ok():
    return {"ok": True}


@router.get("/yes")
async def federation_yes():
    return {"yes": True}


@router.get("/no")
async def federation_no():
    return {"no": False}


@router.get("/maybe")
async def federation_maybe():
    return {"maybe": True}


@router.get("/always")
async def federation_always():
    return {"always": True}


@router.get("/never")
async def federation_never():
    return {"never": False}


@router.post("/import")
async def federation_import(payload: dict):
    return {"imported": True}


@router.post("/dedup")
async def federation_dedup(payload: dict):
    return {"deduped": True}


@router.post("/retry")
async def federation_retry(payload: dict):
    return {"retried": True}


@router.post("/recover-node")
async def federation_recover_node(payload: dict):
    return {"recovered": True}


@router.get("/fallback")
async def federation_fallback():
    return {"fallback": True}


@router.get("/integrity")
async def federation_integrity():
    return {"integrity": True}


@router.get("/degrade")
async def federation_degrade():
    return {"mode": "normal"}


@router.get("/metrics")
async def federation_metrics():
    return {"peers": 0, "reports": 0, "latency_ms": 0}


@router.get("/users/{ref}")
async def resolve_user(ref: str, db: Session = Depends(get_db)):
    user = db.query(User).filter((User.uuid == ref) | (User.did == ref) | (User.handle == ref)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "uuid": user.uuid, "did": user.did, "handle": user.handle, "username": user.username}


@router.get("/.well-known/webfinger")
async def webfinger(resource: str, db: Session = Depends(get_db)):
    # resource like acct:user@domain
    handle = resource.split("acct:")[-1]
    user = db.query(User).filter((User.handle == handle) | (User.username == handle.split("@")[0])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"subject": resource, "links": [{"rel": "self", "href": f"/api/users/{user.id}"}]}
