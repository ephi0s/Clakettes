from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.routers.dependencies import get_or_404
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPublicResponse, UsersPage, UsersPublicPage
from app.services.user_service import UserService
from app.services.notification_service import NotificationService
from app.routers.permissions import can_edit_user, can_delete_user, is_admin
from app.models.user import User

router = APIRouter()
service = UserService()
notification_service = NotificationService()


@router.get("/", response_model=UsersPage | UsersPublicPage)
async def list_users(
    page: int = 1,
    size: int = 20,
    is_active: bool | None = None,
    role: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    page_data = service.get_multi_paginated(db, page=page, size=size, is_active=is_active, role=role)
    if is_admin(current_user):
        return UsersPage(**page_data)
    public_items = [service.to_authenticated_public_response(u) for u in page_data["items"]]
    return UsersPublicPage(**{**page_data, "items": public_items})


@router.get("/public", response_model=list[UserPublicResponse])
async def list_public_users(page: int = 1, size: int = 50, db: Session = Depends(get_db)):
    """List users with only their publicly visible fields."""
    return service.get_public_users(db, page=page, size=size)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Return the full profile of the currently authenticated user."""
    return current_user


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if service.get_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if service.get_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if not is_admin(current_user):
        user = user.model_copy(update={"role": "user"})
    return service.create(db, user)


@router.get("/{user_id}", response_model=UserResponse | UserPublicResponse)
async def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_or_404(db, User, user_id, "User")
    if is_admin(current_user) or current_user.id == user_id:
        return user
    return service.to_authenticated_public_response(user)


@router.get("/{user_id}/public", response_model=UserPublicResponse)
async def get_public_user(user_id: int, db: Session = Depends(get_db)):
    """Return only the publicly visible fields of a user."""
    user = get_or_404(db, User, user_id, "User")
    return service.to_public_response(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    target_user = get_or_404(db, User, user_id, "User")
    if not can_edit_user(db, current_user, target_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    is_other_user = current_user.id != user_id
    updated = service.update(db, user_id, user)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")

    if is_other_user and current_user.role in ("admin", "organizer"):
        editor_name = current_user.full_name or current_user.username
        notification_service.create_notification(
            db,
            user_id=user_id,
            title="Profile updated by team",
            message=f"Your profile has been updated by {editor_name} ({current_user.role}).",
            notification_type="profile_update",
            related_user_id=current_user.id,
        )

    return updated


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    target_user = get_or_404(db, User, user_id, "User")
    if not can_delete_user(db, current_user, target_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and organizers can delete users")
    deleted = service.delete(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
