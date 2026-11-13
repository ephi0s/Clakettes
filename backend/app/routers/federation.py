"""Federation endpoints (node policies: allowlist/blocklist)."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.services.node_policy_service import NodePolicyService

router = APIRouter(prefix="/federation", tags=["federation"])
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
