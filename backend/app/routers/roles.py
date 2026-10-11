"""Router for role, festival role, role dependency, and role conflict management."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RolesPage,
    FestivalRoleCreate,
    FestivalRoleUpdate,
    FestivalRoleResponse,
    FestivalRolesPage,
)
from app.services.role_service import RoleService, FestivalRoleService
from app.services.user_service import UserService
from app.services.festival_service import FestivalService
from app.routers.permissions import is_admin, require_festival_admin
from app.routers.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter()

role_service = RoleService()
festival_role_service = FestivalRoleService()
user_service = UserService()
festival_service = FestivalService()


def require_admin(user: User):
    if not is_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")


@router.get("/roles/", response_model=RolesPage)
async def list_roles(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    scope: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return role_service.get_all_paginated(db, page, size, scope)


@router.post("/roles/", response_model=RoleResponse, status_code=201)
async def create_role(role: RoleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_admin(current_user)
    if role_service.get_by_name(db, role.name):
        raise HTTPException(status_code=400, detail="Role already exists")
    return role_service.create(db, role)


@router.get("/roles/hierarchy/", response_model=list[RoleResponse])
async def get_role_hierarchy(
    db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)
):
    """Returns roles in hierarchy order (highest level first)."""
    return role_service.get_all_ordered_by_hierarchy(db)


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)
):
    role = role_service.get(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int, role: RoleUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    require_admin(current_user)
    role_obj = role_service.get(db, role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    updated = role_service.update(db, role_id, role)
    if not updated:
        raise HTTPException(status_code=404, detail="Role not found")
    return updated


@router.delete("/roles/{role_id}")
async def delete_role(role_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_admin(current_user)
    role_obj = role_service.get(db, role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    deleted = role_service.delete(db, role_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted"}


@router.get("/festivals/{festival_id}/roles/", response_model=FestivalRolesPage)
async def list_festival_roles(
    festival_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    result = festival_role_service.get_by_festival_paginated(db, festival_id, page, size)
    enriched = []
    for fr in result["items"]:
        fr_data = {c.name: getattr(fr, c.name) for c in fr.__table__.columns}
        enriched.append({**fr_data, "role": fr.role})
    return {"items": enriched, "total": result["total"], "page": page, "size": size, "pages": result["pages"]}


@router.post("/festivals/{festival_id}/roles/", response_model=FestivalRoleResponse, status_code=201)
async def create_festival_role(
    festival_id: int,
    fr: FestivalRoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    require_festival_admin(db, current_user, festival_id)
    role_obj = role_service.get(db, fr.role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    fr_data = FestivalRoleCreate(**{**fr.model_dump(), "festival_id": festival_id})
    return role_service.create_festival_role(db, fr_data)


@router.post("/festivals/{festival_id}/roles/initialize", response_model=list[FestivalRoleResponse])
async def initialize_festival_roles(
    festival_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    return festival_role_service.initialize_default_festival_roles(db, festival_id)


@router.put("/festivals/{festival_id}/roles/{fr_id}", response_model=FestivalRoleResponse)
async def update_festival_role(
    festival_id: int,
    fr_id: int,
    fr: FestivalRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    existing = festival_role_service.get(db, fr_id)
    if not existing or existing.festival_id != festival_id:
        raise HTTPException(status_code=404, detail="Festival role not found")
    require_festival_admin(db, current_user, festival_id)
    updated = festival_role_service.update(db, fr_id, fr)
    return updated


@router.delete("/festivals/{festival_id}/roles/{fr_id}")
async def delete_festival_role(
    festival_id: int,
    fr_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    festival = festival_service.get(db, festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    existing = festival_role_service.get(db, fr_id)
    if not existing or existing.festival_id != festival_id:
        raise HTTPException(status_code=404, detail="Festival role not found")
    require_festival_admin(db, current_user, festival_id)
    festival_role_service.delete(db, fr_id)
    return {"message": "Festival role removed"}


@router.get("/roles/{role_id}/dependencies")
async def list_role_dependencies(
    role_id: int, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)
):
    role_obj = role_service.get(db, role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    deps = festival_role_service.get_dependencies(db, role_id)
    return {"items": deps}


@router.post("/role-dependencies/", status_code=201)
async def create_role_dependency(
    role_id: int,
    depends_on_role_id: int,
    dependency_type: str = "required",
    notes: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    return festival_role_service.add_dependency(db, role_id, depends_on_role_id, dependency_type, notes)


@router.delete("/role-dependencies/{dependency_id}")
async def delete_role_dependency(
    dependency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    if not festival_role_service.remove_dependency(db, dependency_id):
        raise HTTPException(status_code=404, detail="Dependency not found")
    return {"message": "Dependency deleted"}


@router.get("/roles/{role_id}/conflicts")
async def list_role_conflicts(
    role_id: int, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)
):
    role_obj = role_service.get(db, role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    conflicts = festival_role_service.get_conflicting_roles(db, role_id)
    return {"items": conflicts}


@router.post("/role-conflicts/", status_code=201)
async def create_role_conflict(
    role_id: int,
    conflicts_with_role_id: int,
    conflict_type: str = "exclusive",
    notes: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    return festival_role_service.add_conflict(db, role_id, conflicts_with_role_id, conflict_type, notes)


@router.delete("/role-conflicts/{conflict_id}")
async def delete_role_conflict(
    conflict_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    if not festival_role_service.remove_conflict(db, conflict_id):
        raise HTTPException(status_code=404, detail="Conflict not found")
    return {"message": "Conflict deleted"}


@router.get("/roles/{role_id}/check-conflicts")
async def check_role_conflicts(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Check if assigning this role to a user would cause conflicts."""
    role_obj = role_service.get(db, role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    user_obj = user_service.get(db, user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "conflicts": festival_role_service.check_role_conflicts(db, user_id, role_id),
        "unfulfilled_dependencies": festival_role_service.check_fulfilled_dependencies(db, user_id, role_id),
    }
