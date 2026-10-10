from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.routers.permissions import is_admin
from app.models.location import Location
from app.routers.dependencies import get_or_404
from app.services.location_tag_service import LocationTagService
from app.services.location_service import LocationService
from app.schemas.location_tag import LocationTagCreate, LocationTagResponse
from app.models.user import User

router = APIRouter()

tag_service = LocationTagService()
location_service = LocationService()


@router.get("/", response_model=list[LocationTagResponse])
async def list_location_tags(location_id: int, db: Session = Depends(get_db)):
    return tag_service.get_by_location(db, location_id)


@router.post("/", response_model=LocationTagResponse, status_code=201)
async def create_location_tag(
    location_id: int,
    tag: LocationTagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_or_404(db, Location, location_id, "Location")
    return tag_service.create_tag(db, location_id, tag, current_user.id, is_admin=is_admin(current_user))


@router.delete("/{tag_id}")
async def revoke_location_tag(
    location_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    tag = tag_service.revoke_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"message": "Tag revoked"}
