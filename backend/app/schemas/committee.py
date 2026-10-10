from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .common import PageBase


class CommitteeBase(BaseModel):
    festival_id: int
    name: str
    description: str | None = None
    role_id: int | None = None
    is_active: bool = True
    max_members: int | None = None
    external_visible: bool = False


class CommitteeCreate(CommitteeBase):
    pass


class CommitteeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    role_id: int | None = None
    is_active: bool | None = None
    max_members: int | None = None
    external_visible: bool | None = None


class CommitteeResponse(CommitteeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    member_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class CommitteePage(PageBase):
    items: list[CommitteeResponse]


class CommitteeMemberBase(BaseModel):
    committee_id: int
    user_id: int
    role_in_committee: str = "member"
    assigned_by: int | None = None
    notes: str | None = None


class CommitteeMemberCreate(CommitteeMemberBase):
    pass


class CommitteeMemberUpdate(BaseModel):
    role_in_committee: str | None = None
    is_active: bool | None = None
    notes: str | None = None


class CommitteeMemberResponse(CommitteeMemberBase):
    id: int
    is_active: bool
    joined_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    user: Optional["UserResponse"] = None
    committee: CommitteeResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class CommitteeMemberPage(PageBase):
    items: list[CommitteeMemberResponse]


from .user import UserResponse  # noqa: E402

CommitteeMemberResponse.model_rebuild()
