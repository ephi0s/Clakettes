"""Router for user follows (social graph)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.routers.dependencies import get_or_404
from app.schemas.user_follow import FollowStatus, UserFollowResponse, UserFollowsPage
from app.services.user_follow_service import UserFollowService

router = APIRouter()

follow_service = UserFollowService()


@router.post("/users/{user_id}/follow", response_model=UserFollowResponse, status_code=201)
async def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    get_or_404(db, User, user_id, "User")
    return follow_service.follow(db, current_user.id, user_id)


@router.delete("/users/{user_id}/follow")
async def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_or_404(db, User, user_id, "User")
    follow_service.unfollow(db, current_user.id, user_id)
    return {"message": "Unfollowed"}


@router.get("/users/{user_id}/follow/status", response_model=FollowStatus)
async def follow_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_or_404(db, User, user_id, "User")
    return follow_service.status(db, user_id, current_user.id)


@router.get("/users/{user_id}/followers", response_model=UserFollowsPage)
async def list_followers(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_or_404(db, User, user_id, "User")
    return follow_service.list_followers(db, user_id, page, size)


@router.get("/users/{user_id}/following", response_model=UserFollowsPage)
async def list_following(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_or_404(db, User, user_id, "User")
    return follow_service.list_following(db, user_id, page, size)
