from fastapi import APIRouter, Query, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.services.user_service import verify_password
from app.services.admin_service import AdminService
from app.services.audit_service import AuditService
from app.schemas.audit_log import AuditLogsPage
from app.rate_limiter import RateLimiter
from app.config import is_testing
from app.routers.permissions import require_admin

router = APIRouter()
admin_service = AdminService()
audit_service = AuditService()
_reset_limiter = RateLimiter()


def _check_reset_rate_limit(user_id: int):
    if is_testing():
        return
    if not _reset_limiter.check(f"reset:{user_id}", 3, 300):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many reset attempts. Try again in 5 minutes.",
        )


class ResetConfirm(BaseModel):
    confirm: str = ""
    password: str = ""


@router.get("/stats")
async def database_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_admin(current_user, db)
    return admin_service.get_stats(db)


@router.get("/tables")
async def list_tables(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_admin(current_user, db)
    return admin_service.get_tables(db)


@router.get("/audit-log", response_model=AuditLogsPage)
async def list_audit_log(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    action: str | None = None,
    actor_user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Append-only record of sensitive actions (RGPD art. 5.2). Admin only."""
    require_admin(current_user, db)
    return audit_service.list_paginated(db, page=page, size=size, action=action, actor_user_id=actor_user_id)


@router.post("/reset")
async def reset_database(
    body: ResetConfirm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user, db)
    _check_reset_rate_limit(current_user.id)
    if body.confirm != "yes":
        raise HTTPException(status_code=400, detail="Send confirm=yes to proceed")
    if not verify_password(body.password, current_user.password_hash):
        raise HTTPException(status_code=403, detail="Invalid password — re-authentication required")
    return admin_service.reset_database(db)
