"""Router for role delegations and role transitions."""

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.schemas.role_delegation import (
    RoleDelegationCreate,
    RoleDelegationUpdate,
    RoleDelegationResponse,
    RoleDelegationPage,
)
from app.schemas.role_transition import (
    RoleTransitionCreate,
    RoleTransitionResponse,
    RoleTransitionPage,
)
from app.services.group_service import RoleDelegationService, RoleTransitionService
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.models.role_delegation import RoleDelegation
from app.routers.permissions import is_admin
from app.routers.dependencies import get_current_user_optional, get_or_404
from app.models.user import User

router = APIRouter()

delegation_service = RoleDelegationService()
transition_service = RoleTransitionService()
user_service = UserService()
role_service = RoleService()


@router.get("/delegations/", response_model=RoleDelegationPage)
async def list_delegations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    delegator_id: int | None = None,
    delegate_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    if (
        current_user is not None
        and not is_admin(current_user)
        and delegator_id not in (None, current_user.id)
        and delegate_id
        not in (
            None,
            current_user.id,
        )
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return delegation_service.get_all_paginated(db, page, size, delegator_id, delegate_id, status)


@router.post("/delegations/", response_model=RoleDelegationResponse, status_code=201)
async def create_delegation(
    obj: RoleDelegationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if obj.delegator_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="You can only create delegations on your own behalf")
    return delegation_service.create(db, obj)


@router.put("/delegations/{delegation_id}", response_model=RoleDelegationResponse)
async def update_delegation(
    delegation_id: int,
    obj: RoleDelegationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_or_404(db, RoleDelegation, delegation_id, "Delegation")
    if existing.delegator_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="You can only update your own delegations")
    updated = delegation_service.update(db, delegation_id, obj)
    if not updated:
        raise HTTPException(status_code=404, detail="Delegation not found")
    return updated


@router.post("/delegations/{delegation_id}/revoke")
async def revoke_delegation(
    delegation_id: int,
    reason: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_or_404(db, RoleDelegation, delegation_id, "Delegation")
    if existing.delegator_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="You can only revoke your own delegations")
    return delegation_service.revoke(db, delegation_id, current_user.id, reason)


@router.get("/users/{user_id}/active-delegations", response_model=list[RoleDelegationResponse])
async def get_user_active_delegations(
    user_id: int,
    direction: str = "received",
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Get active delegations for a user. Direction: 'received' or 'given'."""
    if current_user is not None and user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if direction == "received":
        return delegation_service.get_active_by_delegate(db, user_id)
    return delegation_service.get_active_by_delegator(db, user_id)


@router.get("/role-transitions/", response_model=RoleTransitionPage)
async def list_role_transitions(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: int | None = None,
    transition_type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id is not None and user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return transition_service.get_all_paginated(db, page, size, user_id, transition_type)


@router.post("/role-transitions/", response_model=RoleTransitionResponse, status_code=201)
async def create_role_transition(
    obj: RoleTransitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if obj.user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="You can only create transitions for yourself")
    return transition_service.create(db, obj)


@router.get("/users/{user_id}/role-transitions", response_model=RoleTransitionPage)
async def get_user_role_transitions(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = user_service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return transition_service.get_all_paginated(db, page, size, user_id=user_id)


@router.get("/users/{user_id}/role-check")
async def check_user_role_eligibility(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check if a user can be assigned a role (dependencies + conflicts)."""
    if user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = user_service.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role_obj = role_service.get(db, role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    return {
        "conflicts": role_service.check_role_conflicts(db, user_id, role_id),
        "dependencies": role_service.check_fulfilled_dependencies(db, user_id, role_id),
        "eligible": len(role_service.check_role_conflicts(db, user_id, role_id)) == 0,
    }
