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
    reason: str | None = None


def _require_admin(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")


@router.get("/nodes")
async def list_node_policies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require_admin(current_user)
    return [
        {"id": p.id, "node_domain": p.node_domain, "allowed": p.allowed, "reason": p.reason}
        for p in service.list_policies(db)
    ]


@router.post("/nodes")
async def set_node_policy(
    body: NodePolicyIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    _require_admin(current_user)
    p = service.set_policy(db, body.node_domain, body.allowed, body.consent_required, body.reason)
    return {
        "id": p.id,
        "node_domain": p.node_domain,
        "allowed": p.allowed,
        "consent_required": p.consent_required,
        "reason": p.reason,
    }


@router.get("/manifest")
async def federation_manifest():
    return {"schema_version": "1", "node": "primary", "capabilities": ["festivals", "users", "chat"]}


@router.patch("/reports/{report_id}")
async def update_report_status(report_id: int, status: str, db: Session = Depends(get_db)):
    r = report_service.update_status(db, report_id, status)
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"id": r.id, "status": r.status}


@router.get("/directory")
async def federation_directory():
    return {"nodes": [{"domain": "primary", "schema_version": "1", "status": "online"}]}


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
