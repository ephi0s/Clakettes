from fastapi import APIRouter, Query, Depends, Form, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.schemas.festival_rulebook import (
    FestivalRulebookCreate,
    FestivalRulebookResponse,
    FestivalRulebookUpdate,
    FestivalRulebooksPage,
)
from app.services.festival_rulebook_service import FestivalRulebookService
from app.services.festival_service import FestivalService
from app.services.event_service import EventService
from app.routers.permissions import can_edit_festival, require_festival_admin
from app.routers.uploads import _save_file, ALLOWED_DOC_TYPES, MAX_DOC_SIZE

router = APIRouter()
rulebook_service = FestivalRulebookService()
festival_service = FestivalService()
event_service = EventService()


def _get_festival_or_404(db: Session, festival_id: int):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    return festival


def _check_event_belongs(db: Session, festival_id: int, event_id: int | None):
    if event_id is None:
        return
    event = event_service.get(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.festival_id != festival_id:
        raise HTTPException(status_code=400, detail="Event does not belong to this festival")


def _check_document_present(file_url: str | None, external_url: str | None):
    if not file_url and not external_url:
        raise HTTPException(
            status_code=422,
            detail="Either file_url or external_url must be provided",
        )


@router.get("/", response_model=FestivalRulebooksPage)
async def list_rulebooks(
    festival_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: str | None = None,
    db: Session = Depends(get_db),
):
    _get_festival_or_404(db, festival_id)
    return rulebook_service.get_paginated_by_festival(db, festival_id, page=page, size=size, category=category)


@router.get("/{rulebook_id}", response_model=FestivalRulebookResponse)
async def get_rulebook(festival_id: int, rulebook_id: int, db: Session = Depends(get_db)):
    _get_festival_or_404(db, festival_id)
    rulebook = rulebook_service.get(db, rulebook_id)
    if not rulebook or rulebook.festival_id != festival_id:
        raise HTTPException(status_code=404, detail="Rulebook not found")
    return rulebook


@router.post("/", response_model=FestivalRulebookResponse, status_code=201)
async def create_rulebook(
    festival_id: int,
    data: FestivalRulebookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = _get_festival_or_404(db, festival_id)
    require_festival_admin(db, current_user, festival_id)
    if not can_edit_festival(db, current_user, festival):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    _check_event_belongs(db, festival_id, data.event_id)
    _check_document_present(data.file_url, data.external_url)
    payload = data.model_dump()
    payload["festival_id"] = festival_id
    obj = rulebook_service.model(**payload, created_by=current_user.id, updated_by=current_user.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/upload", response_model=FestivalRulebookResponse, status_code=201)
async def upload_rulebook(
    festival_id: int,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str | None = Form(None),
    category: str = Form("official_section"),
    event_id: int | None = Form(None),
    external_url: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = _get_festival_or_404(db, festival_id)
    require_festival_admin(db, current_user, festival_id)
    if not can_edit_festival(db, current_user, festival):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    _check_event_belongs(db, festival_id, event_id)
    try:
        data = FestivalRulebookCreate(
            title=title,
            description=description,
            category=category,
            event_id=event_id,
            file_url="placeholder",
            external_url=external_url,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    url = await _save_file(file, "rulebooks", ALLOWED_DOC_TYPES, MAX_DOC_SIZE)
    obj = rulebook_service.model(
        festival_id=festival_id,
        title=data.title,
        description=data.description,
        category=data.category,
        event_id=data.event_id,
        file_url=url,
        external_url=data.external_url,
        is_published=True,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/{rulebook_id}", response_model=FestivalRulebookResponse)
async def update_rulebook(
    festival_id: int,
    rulebook_id: int,
    data: FestivalRulebookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = _get_festival_or_404(db, festival_id)
    require_festival_admin(db, current_user, festival_id)
    if not can_edit_festival(db, current_user, festival):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    rulebook = rulebook_service.get(db, rulebook_id)
    if not rulebook or rulebook.festival_id != festival_id:
        raise HTTPException(status_code=404, detail="Rulebook not found")
    if data.event_id is not None:
        _check_event_belongs(db, festival_id, data.event_id)
    update_data = data.model_dump(exclude_unset=True)
    update_data["updated_by"] = current_user.id
    for field, value in update_data.items():
        setattr(rulebook, field, value)
    if not rulebook.file_url and not rulebook.external_url:
        raise HTTPException(
            status_code=422,
            detail="Either file_url or external_url must be provided",
        )
    db.commit()
    db.refresh(rulebook)
    return rulebook


@router.delete("/{rulebook_id}")
async def delete_rulebook(
    festival_id: int,
    rulebook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = _get_festival_or_404(db, festival_id)
    require_festival_admin(db, current_user, festival_id)
    if not can_edit_festival(db, current_user, festival):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    rulebook = rulebook_service.get(db, rulebook_id)
    if not rulebook or rulebook.festival_id != festival_id:
        raise HTTPException(status_code=404, detail="Rulebook not found")
    db.delete(rulebook)
    db.commit()
    return {"message": "Rulebook deleted"}
