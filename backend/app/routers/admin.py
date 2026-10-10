import os

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.services.user_service import verify_password
from app.services.admin_service import AdminService
from app.rate_limiter import RateLimiter

router = APIRouter()
admin_service = AdminService()
_reset_limiter = RateLimiter()


def _check_reset_rate_limit(user_id: int):
    if os.environ.get("TESTING", "").lower() in ("true", "1"):
        return
    if not _reset_limiter.check(f"reset:{user_id}", 3, 300):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many reset attempts. Try again in 5 minutes.",
        )


class ResetConfirm(BaseModel):
    confirm: str = ""
    password: str = ""


def _require_admin(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")


@router.get("/stats")
async def database_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require_admin(current_user)
    return admin_service.get_stats(db)


@router.get("/tables")
async def list_tables(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require_admin(current_user)
    return admin_service.get_tables(db)


@router.post("/reset")
async def reset_database(
    body: ResetConfirm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    _check_reset_rate_limit(current_user.id)
    if body.confirm != "yes":
        raise HTTPException(status_code=400, detail="Send confirm=yes to proceed")
    if not verify_password(body.password, current_user.password_hash):
        raise HTTPException(status_code=403, detail="Invalid password — re-authentication required")
    return admin_service.reset_database(db)
