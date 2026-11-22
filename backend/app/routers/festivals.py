from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.festival import Festival
from app.models.shortfilm import ShortFilm
from app.models.location import Location
from app.models.user_festival import user_festival
from app.routers.dependencies import get_or_404
from app.schemas.festival import (
    FestivalCreate,
    FestivalUpdate,
    FestivalResponse,
    FestivalDetailResponse,
    FestivalsPage,
)
from app.schemas.shortfilm import (
    FestivalShortFilmCreate,
    ShortFilmCreate,
    ShortFilmUpdate,
    ShortFilmResponse,
    ShortFilmsPage,
)
from app.schemas.location import LocationResponse
from app.schemas.festival_location import FestivalLocationCreate
from app.services.festival_service import FestivalService
from app.services.festival_location_service import FestivalLocationService
from app.services.shortfilm_service import ShortFilmService
from app.routers.permissions import (
    can_edit_festival,
    can_delete_festival,
    can_edit_shortfilm,
    can_delete_shortfilm,
)
from app.routers.uploads import _save_file, ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE
from app.models.user import User

router = APIRouter()
service = FestivalService()
festival_location_service = FestivalLocationService()
shortfilm_service = ShortFilmService()


@router.get("/", response_model=FestivalsPage)
async def list_festivals(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    is_active: bool | None = None,
    db: Session = Depends(get_db),
):
    return service.get_multi_paginated(db, page=page, size=size, is_active=is_active)


@router.post("/", response_model=FestivalResponse, status_code=201)
async def create_festival(
    festival: FestivalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    created = service.create(db, festival)
    db.execute(user_festival.insert().values(user_id=current_user.id, festival_id=created.id, role="organizer"))
    db.execute(update(ShortFilm).where(ShortFilm.festival_id.is_(None)).values(festival_id=created.id))
    db.commit()
    return created


@router.get("/{festival_id}", response_model=FestivalDetailResponse)
async def get_festival(festival_id: int, db: Session = Depends(get_db)):
    festival = get_or_404(db, Festival, festival_id, "Festival")
    films = db.query(ShortFilm).filter(ShortFilm.festival_id == festival_id).order_by(ShortFilm.id).all()
    return FestivalDetailResponse.model_validate(festival).model_copy(
        update={"shortfilm_count": len(films), "shortfilms": films}
    )


@router.get("/{festival_id}/shortfilms", response_model=ShortFilmsPage)
async def list_festival_shortfilms(
    festival_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    contest_type: str | None = None,
    db: Session = Depends(get_db),
):
    get_or_404(db, Festival, festival_id, "Festival")
    return shortfilm_service.get_multi_paginated(
        db, page=page, size=size, festival_id=festival_id, contest_type=contest_type
    )


@router.post("/{festival_id}/shortfilms", response_model=ShortFilmResponse, status_code=201)
async def create_festival_shortfilm(
    festival_id: int,
    shortfilm: FestivalShortFilmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_or_404(db, Festival, festival_id, "Festival")
    payload = ShortFilmCreate(**shortfilm.model_dump(), festival_id=festival_id, user_id=current_user.id)
    return shortfilm_service.create(db, payload)


@router.get("/{festival_id}/shortfilms/{shortfilm_id}", response_model=ShortFilmResponse)
async def get_festival_shortfilm(festival_id: int, shortfilm_id: int, db: Session = Depends(get_db)):
    film = get_or_404(db, ShortFilm, shortfilm_id, "Short film")
    if film.festival_id != festival_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short film not found in festival")
    return film


@router.put("/{festival_id}/shortfilms/{shortfilm_id}", response_model=ShortFilmResponse)
async def update_festival_shortfilm(
    festival_id: int,
    shortfilm_id: int,
    shortfilm: ShortFilmUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    film = get_or_404(db, ShortFilm, shortfilm_id, "Short film")
    if film.festival_id != festival_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short film not found in festival")
    if not can_edit_shortfilm(db, current_user, film):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return shortfilm_service.update(db, shortfilm_id, shortfilm)


@router.delete("/{festival_id}/shortfilms/{shortfilm_id}")
async def delete_festival_shortfilm(
    festival_id: int,
    shortfilm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    film = get_or_404(db, ShortFilm, shortfilm_id, "Short film")
    if film.festival_id != festival_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short film not found in festival")
    if not can_delete_shortfilm(db, current_user, film):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    shortfilm_service.delete(db, shortfilm_id)
    return {"message": "Short film deleted"}


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
