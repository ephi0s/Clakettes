from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.shortfilm import ShortFilm
from app.routers.dependencies import get_or_404
from app.schemas.shortfilm_location import ShortFilmLocationCreate, ShortFilmLocationUpdate, ShortFilmLocationResponse
from app.services.shortfilm_location_service import ShortFilmLocationService
from app.services.shortfilm_service import ShortFilmService
from app.routers.permissions import can_edit_shortfilm
from app.models.user import User

router = APIRouter()
service = ShortFilmLocationService()
shortfilm_service = ShortFilmService()


@router.get("/", response_model=list[ShortFilmLocationResponse])
async def list_locations(shortfilm_id: int, db: Session = Depends(get_db)):
    return service.get_by_shortfilm(db, shortfilm_id)


@router.post("/", response_model=ShortFilmLocationResponse, status_code=201)
async def add_location(
    shortfilm_id: int,
    data: ShortFilmLocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    shortfilm = get_or_404(db, ShortFilm, shortfilm_id, "Short film")
    if not can_edit_shortfilm(db, current_user, shortfilm):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    try:
        return service.create_link(db, shortfilm_id, data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.put("/{sfloc_id}", response_model=ShortFilmLocationResponse)
async def update_location(
    shortfilm_id: int,
    sfloc_id: int,
    data: ShortFilmLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    shortfilm = get_or_404(db, ShortFilm, shortfilm_id, "Short film")
    if not can_edit_shortfilm(db, current_user, shortfilm):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    updated = service.update_link(db, sfloc_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Film-location link not found")
    return updated


@router.delete("/{sfloc_id}")
async def remove_location(
    shortfilm_id: int,
    sfloc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    shortfilm = get_or_404(db, ShortFilm, shortfilm_id, "Short film")
    if not can_edit_shortfilm(db, current_user, shortfilm):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    deleted = service.delete(db, sfloc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Film-location link not found")
    return {"message": "Location removed from film"}
