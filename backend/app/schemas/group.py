from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .common import PageBase


class GroupBase(BaseModel):
    name: str
    description: str | None = None
    max_members: int | None = 50


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    max_members: int | None = None


class GroupMemberResponse(BaseModel):
    id: int
    group_id: int
    user_id: int
    role: str
    joined_at: datetime | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class GroupResponse(GroupBase):
    id: int
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    member_count: int | None = 0

    model_config = ConfigDict(from_attributes=True)


class GroupsPage(PageBase):
    items: list[GroupResponse]
