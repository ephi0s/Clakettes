"""Router for user blocking (RGPD / safety)."""

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.schemas.user_block import (
    UserBlockCreate,
    UserBlockResponse,
    UserBlocksPage,
)
from app.services.user_block_service import UserBlockService
from app.models.user import User
from app.routers.dependencies import get_or_404
from app.routers.permissions import can_edit_user

router = APIRouter()

user_block_service = UserBlockService()


@router.post("/users/{user_id}/blocks/", response_model=UserBlockResponse, status_code=201)
async def block_user(
    user_id: int,
    body: UserBlockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_or_404(db, User, user_id, "User")
    get_or_404(db, User, body.blocked_id, "User")
    target = db.get(User, user_id)
    if current_user.id != user_id and not can_edit_user(db, current_user, target):
        raise HTTPException(status_code=403, detail="Not allowed")
    if body.blocked_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot block yourself")
    return user_block_service.block(db, user_id, body.blocked_id, body.reason)


@router.delete("/users/{user_id}/blocks/{blocked_id}")
async def unblock_user(
    user_id: int,
    blocked_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_or_404(db, User, user_id, "User")
    target = db.get(User, user_id)
    if current_user.id != user_id and not can_edit_user(db, current_user, target):
        raise HTTPException(status_code=403, detail="Not allowed")
    ok = user_block_service.unblock(db, user_id, blocked_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Block not found")
    return {"message": "Unblocked"}


@router.get("/users/{user_id}/blocks/", response_model=UserBlocksPage)
async def list_blocked_users(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_or_404(db, User, user_id, "User")
    target = db.get(User, user_id)
    if current_user.id != user_id and not can_edit_user(db, current_user, target):
        raise HTTPException(status_code=403, detail="Not allowed")
    return user_block_service.list_blocked(db, user_id, page, size)


@router.get("/users/{user_id}/blocks/{blocked_id}/status")
async def block_status(
    user_id: int,
    blocked_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_or_404(db, User, user_id, "User")
    return {"blocked": user_block_service.is_blocked(db, user_id, blocked_id)}
