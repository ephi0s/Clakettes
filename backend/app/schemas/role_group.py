from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .common import PageBase


class RoleGroupBase(BaseModel):
    name: str
    display_name: str
    description: str | None = None
    sort_order: int = 0
    is_active: bool = True


class RoleGroupCreate(RoleGroupBase):
    pass


class RoleGroupUpdate(BaseModel):
    display_name: str | None = None
    description: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class RoleGroupResponse(RoleGroupBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleGroupPage(PageBase):
    items: list[RoleGroupResponse]


class RoleGroupMembershipBase(BaseModel):
    group_id: int
    role_id: int
    level: int = 0
    is_leader: bool = False


class RoleGroupMembershipCreate(RoleGroupMembershipBase):
    pass


class RoleGroupMembershipUpdate(BaseModel):
    level: int | None = None
    is_leader: bool | None = None
    is_active: bool | None = None


class RoleGroupMembershipResponse(RoleGroupMembershipBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    group: RoleGroupResponse | None = None
    role: Optional["RoleResponse"] = None

    model_config = ConfigDict(from_attributes=True)


class RoleGroupMembershipPage(PageBase):
    items: list[RoleGroupMembershipResponse]


from .role import RoleResponse  # noqa: E402

RoleGroupMembershipResponse.model_rebuild()
