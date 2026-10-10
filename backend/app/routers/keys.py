from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.database import get_db
from app.models.user import User as UserModel
from app.schemas.user_key import UserKeyUpload, UserKeyResponse
from app.services.user_key_service import UserKeyService

router = APIRouter()
user_key_service = UserKeyService()


@router.post("/me/public-key", response_model=UserKeyResponse)
async def upload_public_key(
    data: UserKeyUpload,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return user_key_service.set_or_update_public_key(db, current_user.id, data)


@router.get("/{user_id}/public-key", response_model=UserKeyResponse)
async def get_public_key(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    key_entry = user_key_service.get_by_user(db, user_id)
    if not key_entry:
        raise HTTPException(status_code=404, detail="User has no public key")
    return key_entry
