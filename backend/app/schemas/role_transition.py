from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .common import PageBase


class RoleTransitionBase(BaseModel):
    user_id: int
    from_role_id: int | None = None
    to_role_id: int
    from_festival_id: int | None = None
    to_festival_id: int | None = None
    transition_type: str  # promotion, demotion, transfer, suspension, reactivation, creation
    changed_by: int
    reason: str | None = None


class RoleTransitionCreate(RoleTransitionBase):
    pass


class RoleTransitionResponse(RoleTransitionBase):
    id: int
    transitioned_at: datetime
    created_at: datetime
    user: Optional["UserResponse"] = None
    from_role: Optional["RoleResponse"] = None
    to_role: Optional["RoleResponse"] = None

    model_config = ConfigDict(from_attributes=True)


class RoleTransitionPage(PageBase):
    items: list[RoleTransitionResponse]


from .user import UserResponse  # noqa: E402
from .role import RoleResponse  # noqa: E402

RoleTransitionResponse.model_rebuild()
