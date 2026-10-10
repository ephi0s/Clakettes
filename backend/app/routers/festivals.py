from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.festival import Festival
from app.models.location import Location
from app.routers.dependencies import get_or_404
from app.schemas.festival import FestivalCreate, FestivalUpdate, FestivalResponse, FestivalsPage
from app.schemas.location import LocationResponse
from app.schemas.festival_location import FestivalLocationCreate
from app.services.festival_service import FestivalService
from app.services.festival_location_service import FestivalLocationService
from app.services.location_service import LocationService
from app.routers.permissions import can_edit_festival, can_delete_festival
from app.routers.uploads import _save_file, ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE
from app.models.user import User

router = APIRouter()
service = FestivalService()
festival_location_service = FestivalLocationService()
location_service = LocationService()


@router.get("/", response_model=FestivalsPage)
async def list_festivals(page: int = 1, size: int = 20, is_active: bool | None = None, db: Session = Depends(get_db)):
    return service.get_multi_paginated(db, page=page, size=size, is_active=is_active)


@router.post("/", response_model=FestivalResponse, status_code=201)
async def create_festival(
    festival: FestivalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return service.create(db, festival)


@router.get("/{festival_id}", response_model=FestivalResponse)
async def get_festival(festival_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Festival, festival_id, "Festival")


@router.put("/{festival_id}", response_model=FestivalResponse)
async def update_festival(
    festival_id: int,
    festival: FestivalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_or_404(db, Festival, festival_id, "Festival")
    if not can_edit_festival(db, current_user, existing):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    updated = service.update(db, festival_id, festival)
    if not updated:
        raise HTTPException(status_code=404, detail="Festival not found")
    return updated


@router.delete("/{festival_id}")
async def delete_festival(
    festival_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    existing = get_or_404(db, Festival, festival_id, "Festival")
    if not can_delete_festival(db, current_user, existing):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    deleted = service.delete(db, festival_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Festival not found")
    return {"message": "Festival deleted"}


@router.post("/{festival_id}/images", response_model=FestivalResponse)
async def upload_festival_image(
    festival_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_or_404(db, Festival, festival_id, "Festival")
    if not can_edit_festival(db, current_user, existing):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    url = await _save_file(file, "festivals", ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)
    images = list(existing.images or [])
    images.append(url)
    updated = service.update(db, festival_id, FestivalUpdate(images=images))
    return updated


@router.delete("/{festival_id}/images", response_model=FestivalResponse)
async def delete_festival_image(
    festival_id: int, url: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    existing = get_or_404(db, Festival, festival_id, "Festival")
    if not can_edit_festival(db, current_user, existing):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    images = list(existing.images or [])
    if url not in images:
        raise HTTPException(status_code=404, detail="Image not found")
    images.remove(url)
    updated = service.update(db, festival_id, FestivalUpdate(images=images))
    return updated


@router.get("/{festival_id}/locations", response_model=list[LocationResponse])
async def list_festival_locations(festival_id: int, db: Session = Depends(get_db)):
    get_or_404(db, Festival, festival_id, "Festival")
    return festival_location_service.get_locations_by_festival(db, festival_id)


@router.post("/{festival_id}/locations", response_model=LocationResponse, status_code=201)
async def add_festival_location(
    festival_id: int,
    data: FestivalLocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_or_404(db, Festival, festival_id, "Festival")
    if not can_edit_festival(db, current_user, existing):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    location = get_or_404(db, Location, data.location_id, "Location")
    try:
        festival_location_service.link(db, festival_id, data.location_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return location


@router.delete("/{festival_id}/locations/{location_id}")
async def remove_festival_location(
    festival_id: int,
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_or_404(db, Festival, festival_id, "Festival")
    if not can_edit_festival(db, current_user, existing):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    removed = festival_location_service.unlink(db, festival_id, location_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Location not linked to this festival")
    return {"message": "Location removed from festival"}
