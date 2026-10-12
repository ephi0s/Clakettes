from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.festival import Festival
from app.routers.dependencies import get_or_404
from app.routers.permissions import is_admin
from app.services.user_festival_service import UserFestivalService
from app.services.festival_service import FestivalService
from app.services.user_service import UserService

router = APIRouter()
user_festival_service = UserFestivalService()
festival_service = FestivalService()
user_service = UserService()


@router.post("/{festival_id}/join")
async def join_festival(
    festival_id: int, role: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    festival = get_or_404(db, Festival, festival_id, "Festival")
    allowed_roles = {"attendee"}
    if role is not None and not is_admin(current_user) and role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not allowed for self join")
    if user_festival_service.is_member(db, current_user.id, festival_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already a member of this festival")
    user_festival_service.join_festival(db, current_user.id, festival_id, role)
    return {"message": f"Joined festival '{festival.name}'"}


@router.delete("/{festival_id}/leave")
async def leave_festival(
    festival_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if not user_festival_service.leave_festival(db, current_user.id, festival_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not a member of this festival")
    return {"message": "Left festival"}


@router.get("/{festival_id}/members")
async def list_festival_members(
    festival_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if not festival_service.get(db, festival_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Festival not found")
    members = user_festival_service.get_festival_members(db, festival_id)
    return {"festival_id": festival_id, "members": members, "total": len(members)}


@router.get("/user/{user_id}/festivals")
async def list_user_festivals(
    user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if not user_service.get(db, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    festivals = user_festival_service.get_user_festivals(db, user_id)
    return {"user_id": user_id, "festivals": festivals, "total": len(festivals)}
