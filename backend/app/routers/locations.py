from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.location import Location
from app.routers.dependencies import get_or_404
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse, LocationDetailResponse, LocationsPage
from app.services.location_service import LocationService
from app.routers.permissions import is_admin, require_location_admin
from app.models.user import User

router = APIRouter()
service = LocationService()


@router.get("/", response_model=LocationsPage)
async def list_locations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    tag: str | None = None,
    is_active: bool | None = None,
    badge: str | None = None,
    db: Session = Depends(get_db),
):
    return service.get_multi_paginated(
        db,
        page=page,
        size=size,
        search=search,
        tag=tag,
        is_active=is_active,
        badge=badge,
    )


@router.post("/", response_model=LocationResponse, status_code=201)
async def create_location(
    location: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.location import Location as LocationModel

    obj_data = location.model_dump()
    obj_data["added_by"] = current_user.id
    db_obj = LocationModel(**obj_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.get("/{location_id}", response_model=LocationDetailResponse)
async def get_location(location_id: int, db: Session = Depends(get_db)):
    location = service.get_with_details(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.put("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int,
    location: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_or_404(db, Location, location_id, "Location")
    require_location_admin(db, current_user, existing)
    updated = service.update(db, location_id, location)
    if not updated:
        raise HTTPException(status_code=404, detail="Location not found")
    return updated


@router.put("/{location_id}/badge", response_model=LocationResponse)
async def update_location_badge(
    location_id: int,
    badge: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    get_or_404(db, Location, location_id, "Location")
    updated = service.update(db, location_id, LocationUpdate(badge=badge))
    return updated


@router.delete("/{location_id}")
async def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_or_404(db, Location, location_id, "Location")
    require_location_admin(db, current_user, existing)
    deleted = service.delete(db, location_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"message": "Location deleted"}
