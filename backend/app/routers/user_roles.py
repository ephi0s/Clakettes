"""Router for user role and user participant tag management."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.schemas.user_role import (
    UserRoleCreate,
    UserRoleUpdate,
    UserRoleResponse,
    UserRolesPage,
    UserParticipantTagCreate,
    UserParticipantTagResponse,
    UserParticipantTagsPage,
)
from app.services.role_service import RoleService, UserRoleService
from app.services.user_service import UserService
from app.services.festival_service import FestivalService
from app.services.participant_tag_service import ParticipantTagService, UserParticipantTagService
from app.routers.permissions import is_admin, require_role_scope_admin
from app.models.user import User

router = APIRouter()

user_service = UserService()
role_service = RoleService()
user_role_service = UserRoleService()
festival_service = FestivalService()
participant_tag_service = ParticipantTagService()
user_participant_tag_service = UserParticipantTagService()


@router.get("/users/{user_id}/roles/", response_model=UserRolesPage)
async def list_user_roles(
    user_id: int,
    page: int = 1,
    size: int = 20,
    festival_id: int | None = None,
    include_hidden: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = user_service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="You can only view your own roles")
    show_hidden = include_hidden if is_admin(current_user) else False
    result = user_role_service.get_by_user_paginated(db, user_id, page, size, festival_id, show_hidden)
    enriched = []
    for ur in result["items"]:
        ur_data = {c.name: getattr(ur, c.name) for c in ur.__table__.columns}
        enriched.append({**ur_data, "role": ur.role})
    return {"items": enriched, "total": result["total"], "page": page, "size": size, "pages": result["pages"]}


@router.post("/users/{user_id}/roles/", response_model=UserRoleResponse, status_code=201)
async def assign_user_role(
    user_id: int,
    ur: UserRoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_obj = user_service.get(db, user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    require_role_scope_admin(db, current_user, ur.festival_id)
    role_obj = role_service.get(db, ur.role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    data = ur.model_dump()
    data["user_id"] = user_id
    data["assigned_by"] = current_user.id
    if ur.festival_id:
        festival = festival_service.get(db, ur.festival_id)
        if not festival:
            raise HTTPException(status_code=404, detail="Festival not found")
    existing = user_role_service.get_by_user(db, user_id)
    for r in existing:
        if r.role_id == ur.role_id and r.festival_id == ur.festival_id:
            raise HTTPException(status_code=400, detail="User already has this role in this scope")
    create_data = UserRoleCreate(**data)
    return user_role_service.create(db, create_data)


@router.put("/users/{user_id}/roles/{ur_id}", response_model=UserRoleResponse)
async def update_user_role(
    user_id: int,
    ur_id: int,
    ur: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = user_service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing = user_role_service.get(db, ur_id)
    if not existing or existing.user_id != user_id:
        raise HTTPException(status_code=404, detail="User role not found")
    require_role_scope_admin(db, current_user, existing.festival_id)
    updated = user_role_service.update(db, ur_id, ur)
    return updated


@router.delete("/users/{user_id}/roles/{ur_id}")
async def remove_user_role(
    user_id: int,
    ur_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = user_service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing = user_role_service.get(db, ur_id)
    if not existing or existing.user_id != user_id:
        raise HTTPException(status_code=404, detail="User role not found")
    require_role_scope_admin(db, current_user, existing.festival_id)
    user_role_service.delete(db, ur_id)
    return {"message": "Role removed from user"}


@router.get("/users/{user_id}/participant-tags/", response_model=UserParticipantTagsPage)
async def list_user_participant_tags(
    user_id: int,
    page: int = 1,
    size: int = 20,
    festival_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = user_service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="You can only view your own participant tags")
    result = user_participant_tag_service.get_by_user_paginated(db, user_id, page, size, festival_id)
    enriched = []
    for upt in result["items"]:
        upt_data = {c.name: getattr(upt, c.name) for c in upt.__table__.columns}
        enriched.append({**upt_data, "tag": upt.tag})
    return {"items": enriched, "total": result["total"], "page": page, "size": size, "pages": result["pages"]}


@router.post("/users/{user_id}/participant-tags/", response_model=UserParticipantTagResponse, status_code=201)
async def assign_user_participant_tag(
    user_id: int,
    upt: UserParticipantTagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = user_service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    require_role_scope_admin(db, current_user, upt.festival_id)
    tag = participant_tag_service.get(db, upt.tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    data = upt.model_dump()
    data["user_id"] = user_id
    data["assigned_by"] = current_user.id
    existing = user_participant_tag_service.get_by_user_and_tag(db, user_id, upt.tag_id, upt.festival_id)
    if existing:
        raise HTTPException(status_code=400, detail="User already has this tag in this scope")
    create_data = UserParticipantTagCreate(**data)
    return user_participant_tag_service.create(db, create_data)


@router.delete("/users/{user_id}/participant-tags/{upt_id}")
async def remove_user_participant_tag(
    user_id: int,
    upt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = user_service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing = user_participant_tag_service.get(db, upt_id)
    if not existing or existing.user_id != user_id:
        raise HTTPException(status_code=404, detail="User tag not found")
    require_role_scope_admin(db, current_user, existing.festival_id)
    user_participant_tag_service.delete(db, upt_id)
    return {"message": "Tag removed from user"}
