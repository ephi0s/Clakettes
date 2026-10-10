"""Router for role groups and role group memberships."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.schemas.role_group import (
    RoleGroupCreate,
    RoleGroupUpdate,
    RoleGroupResponse,
    RoleGroupPage,
    RoleGroupMembershipCreate,
    RoleGroupMembershipUpdate,
    RoleGroupMembershipResponse,
    RoleGroupMembershipPage,
)
from app.services.group_service import RoleGroupService, RoleGroupMembershipService
from app.services.role_service import RoleService
from app.routers.permissions import is_admin
from app.models.user import User

router = APIRouter()

role_group_service = RoleGroupService()
role_group_membership_service = RoleGroupMembershipService()
role_service = RoleService()


def require_admin(user: User):
    if not is_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")


@router.get("/role-groups/", response_model=RoleGroupPage)
async def list_role_groups(
    page: int = 1,
    size: int = 20,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
):
    return role_group_service.get_all_paginated(db, page, size, is_active)


@router.post("/role-groups/", response_model=RoleGroupResponse, status_code=201)
async def create_role_group(
    obj: RoleGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    return role_group_service.create(db, obj)


@router.get("/role-groups/{group_id}", response_model=RoleGroupResponse)
async def get_role_group(group_id: int, db: Session = Depends(get_db)):
    group = role_group_service.get(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Role group not found")
    return group


@router.put("/role-groups/{group_id}", response_model=RoleGroupResponse)
async def update_role_group(
    group_id: int,
    obj: RoleGroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    existing = role_group_service.get(db, group_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Role group not found")
    return role_group_service.update(db, group_id, obj)


@router.delete("/role-groups/{group_id}")
async def delete_role_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    deleted = role_group_service.delete(db, group_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role group not found")
    return {"message": "Role group deleted"}


@router.get("/role-groups/{group_id}/memberships/", response_model=RoleGroupMembershipPage)
async def list_group_memberships(
    group_id: int,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
):
    group = role_group_service.get(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Role group not found")
    return role_group_membership_service.get_by_group_paginated(db, group_id, page, size)


@router.post("/role-groups/{group_id}/memberships/", response_model=RoleGroupMembershipResponse, status_code=201)
async def create_group_membership(
    group_id: int,
    obj: RoleGroupMembershipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    group = role_group_service.get(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Role group not found")
    role_obj = role_service.get(db, obj.role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    data = obj.model_dump()
    data["group_id"] = group_id
    create_data = RoleGroupMembershipCreate(**data)
    return role_group_membership_service.create(db, create_data)


@router.put("/role-group-memberships/{membership_id}", response_model=RoleGroupMembershipResponse)
async def update_group_membership(
    membership_id: int,
    obj: RoleGroupMembershipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    updated = role_group_membership_service.update(db, membership_id, obj)
    if not updated:
        raise HTTPException(status_code=404, detail="Membership not found")
    return updated


@router.delete("/role-group-memberships/{membership_id}")
async def delete_group_membership(
    membership_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    deleted = role_group_membership_service.delete(db, membership_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Membership not found")
    return {"message": "Membership deleted"}
