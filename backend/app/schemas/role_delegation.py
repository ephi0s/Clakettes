from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .common import PageBase


class RoleDelegationBase(BaseModel):
    delegator_id: int
    delegate_id: int
    role_id: int
    festival_id: int | None = None
    status: str = "active"
    starts_at: datetime | None = None
    expires_at: datetime | None = None
    reason: str | None = None
    scope_limitations: str | None = None


class RoleDelegationCreate(RoleDelegationBase):
    pass


class RoleDelegationUpdate(BaseModel):
    status: str | None = None
    expires_at: datetime | None = None
    reason: str | None = None
    scope_limitations: str | None = None
    revoked_reason: str | None = None


class RoleDelegationResponse(RoleDelegationBase):
    id: int
    revoked_by: int | None = None
    revoked_at: datetime | None = None
    revoked_reason: str | None = None
    created_at: datetime
    updated_at: datetime
    delegator: Optional["UserResponse"] = None
    delegate: Optional["UserResponse"] = None
    role: Optional["RoleResponse"] = None
    festival: Optional["FestivalResponse"] = None

    model_config = ConfigDict(from_attributes=True)


class RoleDelegationPage(PageBase):
    items: list[RoleDelegationResponse]


from .user import UserResponse  # noqa: E402
from .role import RoleResponse  # noqa: E402
from .festival import FestivalResponse  # noqa: E402

RoleDelegationResponse.model_rebuild()
