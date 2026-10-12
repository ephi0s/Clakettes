from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.shortfilm import ShortFilm
from app.routers.dependencies import get_or_404
from app.schemas.shortfilm import ShortFilmCreate, ShortFilmUpdate, ShortFilmResponse, ShortFilmsPage
from app.services.shortfilm_service import ShortFilmService
from app.routers.permissions import can_edit_shortfilm, can_delete_shortfilm
from app.models.user import User

router = APIRouter()
service = ShortFilmService()


@router.get("/", response_model=ShortFilmsPage)
async def list_shortfilms(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    festival_id: int | None = None,
    user_id: int | None = None,
    is_public: bool | None = None,
    db: Session = Depends(get_db),
):
    return service.get_multi_paginated(
        db, page=page, size=size, festival_id=festival_id, user_id=user_id, is_public=is_public
    )


@router.post("/", response_model=ShortFilmResponse, status_code=201)
async def create_shortfilm(
    shortfilm: ShortFilmCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return service.create(db, shortfilm)


@router.get("/{shortfilm_id}", response_model=ShortFilmResponse)
async def get_shortfilm(shortfilm_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, ShortFilm, shortfilm_id, "Short film")


@router.put("/{shortfilm_id}", response_model=ShortFilmResponse)
async def update_shortfilm(
    shortfilm_id: int,
    shortfilm: ShortFilmUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_or_404(db, ShortFilm, shortfilm_id, "Short film")
    if not can_edit_shortfilm(db, current_user, existing):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    updated = service.update(db, shortfilm_id, shortfilm)
    if not updated:
        raise HTTPException(status_code=404, detail="Short film not found")
    return updated


@router.delete("/{shortfilm_id}")
async def delete_shortfilm(
    shortfilm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    existing = get_or_404(db, ShortFilm, shortfilm_id, "Short film")
    if not can_delete_shortfilm(db, current_user, existing):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    deleted = service.delete(db, shortfilm_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Short film not found")
    return {"message": "Short film deleted"}
