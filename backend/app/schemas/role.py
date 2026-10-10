from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .common import PageBase
from app.enums import RoleScope


class RoleBase(BaseModel):
    name: str
    display_name: str
    description: str | None = None
    scope: str = RoleScope.FESTIVAL.value
    hierarchy_level: int = 0
    parent_role_id: int | None = None
    group_id: int | None = None
    is_assignable_by_admin: bool = True
    requires_approval: bool = False
    is_active: bool = True
    permissions: str | None = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    display_name: str | None = None
    description: str | None = None
    scope: str | None = None
    hierarchy_level: int | None = None
    parent_role_id: int | None = None
    group_id: int | None = None
    is_assignable_by_admin: bool | None = None
    requires_approval: bool | None = None
    is_active: bool | None = None
    permissions: str | None = None


class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    child_roles: list["RoleResponse"] = []
    group: Optional["RoleGroupResponse"] = None

    model_config = ConfigDict(from_attributes=True)


class RoleHierarchyResponse(BaseModel):
    """Role with full hierarchy tree."""

    role: RoleResponse
    children: list["RoleHierarchyResponse"] = []


class FestivalRoleBase(BaseModel):
    festival_id: int
    role_id: int
    is_active: bool = True
    custom_permissions: str | None = None
    max_assignees: int | None = None


class FestivalRoleCreate(FestivalRoleBase):
    pass


class FestivalRoleUpdate(BaseModel):
    is_active: bool | None = None
    custom_permissions: str | None = None
    max_assignees: int | None = None


class FestivalRoleResponse(FestivalRoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    role: RoleResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class FestivalRolesPage(PageBase):
    items: list[FestivalRoleResponse]


class RolesPage(PageBase):
    items: list[RoleResponse]


# Forward references
from .role_group import RoleGroupResponse  # noqa: E402

RoleResponse.model_rebuild()
RoleHierarchyResponse.model_rebuild()
