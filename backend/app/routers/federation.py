"""Federation endpoints (node policies: allowlist/blocklist)."""

import os

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.rate_limiter import RateLimiter
from app.services.node_policy_service import NodePolicyService

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


class NodePolicyIn(BaseModel):
    node_domain: str
    allowed: bool = True
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
    p = service.set_policy(db, body.node_domain, body.allowed, body.reason)
    return {"id": p.id, "node_domain": p.node_domain, "allowed": p.allowed, "reason": p.reason}


@router.get("/manifest")
async def federation_manifest():
    return {"schema_version": "1", "node": "primary", "capabilities": ["festivals", "users", "chat"]}


@router.get("/directory")
async def federation_directory():
    return {"nodes": [{"domain": "primary", "schema_version": "1", "status": "online"}]}
