"""Router for participant tag management."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.schemas.participant_tag import (
    ParticipantTagCreate,
    ParticipantTagUpdate,
    ParticipantTagResponse,
    ParticipantTagsPage,
    FestivalParticipantTagCreate,
    FestivalParticipantTagUpdate,
    FestivalParticipantTagResponse,
    FestivalParticipantTagsPage,
)
from app.services.participant_tag_service import ParticipantTagService, FestivalParticipantTagService
from app.services.festival_service import FestivalService
from app.routers.permissions import require_admin, require_festival_admin
from app.models.user import User

router = APIRouter()

tag_service = ParticipantTagService()
festival_tag_service = FestivalParticipantTagService()
festival_service = FestivalService()


@router.get("/participant-tags/", response_model=ParticipantTagsPage)
async def list_participant_tags(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: str | None = None,
    db: Session = Depends(get_db),
):
    return tag_service.get_all_paginated(db, page, size, category)


@router.post("/participant-tags/", response_model=ParticipantTagResponse, status_code=201)
async def create_participant_tag(
    tag: ParticipantTagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    if tag_service.get_by_name(db, tag.name):
        raise HTTPException(status_code=400, detail="Tag already exists")
    return tag_service.create(db, tag)


@router.get("/participant-tags/{tag_id}", response_model=ParticipantTagResponse)
async def get_participant_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = tag_service.get(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.put("/participant-tags/{tag_id}", response_model=ParticipantTagResponse)
async def update_participant_tag(
    tag_id: int,
    tag: ParticipantTagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    updated = tag_service.update(db, tag_id, tag)
    if not updated:
        raise HTTPException(status_code=404, detail="Tag not found")
    return updated


@router.delete("/participant-tags/{tag_id}")
async def delete_participant_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    deleted = tag_service.delete(db, tag_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"message": "Tag deleted"}


@router.get("/festivals/{festival_id}/participant-tags/", response_model=FestivalParticipantTagsPage)
async def list_festival_participant_tags(
    festival_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    result = festival_tag_service.get_by_festival_paginated(db, festival_id, page, size)
    enriched = []
    for fpt in result["items"]:
        fpt_data = {c.name: getattr(fpt, c.name) for c in fpt.__table__.columns}
        enriched.append({**fpt_data, "tag": fpt.tag})
    return {"items": enriched, "total": result["total"], "page": page, "size": size, "pages": result["pages"]}


@router.post(
    "/festivals/{festival_id}/participant-tags/", response_model=FestivalParticipantTagResponse, status_code=201
)
async def create_festival_participant_tag(
    festival_id: int,
    fpt: FestivalParticipantTagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    require_festival_admin(db, current_user, festival_id)
    tag = tag_service.get(db, fpt.tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    data = fpt.model_dump()
    data["festival_id"] = festival_id
    existing = festival_tag_service.get_by_festival_and_tag(db, festival_id, fpt.tag_id)
    if existing:
        raise HTTPException(status_code=400, detail="Festival tag already configured")
    create_data = FestivalParticipantTagCreate(**data)
    return festival_tag_service.create(db, create_data)


@router.put("/festivals/{festival_id}/participant-tags/{fpt_id}", response_model=FestivalParticipantTagResponse)
async def update_festival_participant_tag(
    festival_id: int,
    fpt_id: int,
    fpt: FestivalParticipantTagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    existing = festival_tag_service.get(db, fpt_id)
    if not existing or existing.festival_id != festival_id:
        raise HTTPException(status_code=404, detail="Festival tag not found")
    require_festival_admin(db, current_user, festival_id)
    updated = festival_tag_service.update(db, fpt_id, fpt)
    return updated


@router.delete("/festivals/{festival_id}/participant-tags/{fpt_id}")
async def delete_festival_participant_tag(
    festival_id: int,
    fpt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    existing = festival_tag_service.get(db, fpt_id)
    if not existing or existing.festival_id != festival_id:
        raise HTTPException(status_code=404, detail="Festival tag not found")
    require_festival_admin(db, current_user, festival_id)
    festival_tag_service.delete(db, fpt_id)
    return {"message": "Festival tag removed"}
