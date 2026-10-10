from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .common import PageBase
from app.enums import UserRoleStatus, UserRoleVisibility


class UserRoleBase(BaseModel):
    user_id: int
    role_id: int
    festival_id: int | None = None
    status: str = UserRoleStatus.PENDING.value
    visibility: str = UserRoleVisibility.PUBLIC.value
    is_primary: bool = False
    is_hidden: bool = False
    assigned_by: int | None = None
    approved_by: int | None = None
    start_date: datetime | None = None
    expires_at: datetime | None = None
    invitation_note: str | None = None
    notes: str | None = None


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(BaseModel):
    status: str | None = None
    visibility: str | None = None
    is_primary: bool | None = None
    is_hidden: bool | None = None
    approved_by: int | None = None
    start_date: datetime | None = None
    expires_at: datetime | None = None
    invitation_note: str | None = None
    notes: str | None = None


class UserRoleResponse(UserRoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    approved_at: datetime | None = None
    role: Optional["RoleResponse"] = None
    festival: Optional["FestivalResponse"] = None

    model_config = ConfigDict(from_attributes=True)


class UserRolesPage(PageBase):
    items: list[UserRoleResponse]


class UserParticipantTagBase(BaseModel):
    user_id: int
    tag_id: int
    festival_id: int | None = None
    is_primary: bool = False
    assigned_by: int | None = None
    notes: str | None = None
    is_hidden: bool = False


class UserParticipantTagCreate(UserParticipantTagBase):
    pass


class UserParticipantTagUpdate(BaseModel):
    is_primary: bool | None = None
    notes: str | None = None
    is_hidden: bool | None = None


class UserParticipantTagResponse(UserParticipantTagBase):
    id: int
    created_at: datetime
    updated_at: datetime
    tag: Optional["ParticipantTagResponse"] = None
    festival: Optional["FestivalResponse"] = None

    model_config = ConfigDict(from_attributes=True)


class UserParticipantTagsPage(PageBase):
    items: list[UserParticipantTagResponse]


# Forward references
from .role import RoleResponse  # noqa: E402
from .festival import FestivalResponse  # noqa: E402
from .participant_tag import ParticipantTagResponse  # noqa: E402

UserRoleResponse.model_rebuild()
UserParticipantTagResponse.model_rebuild()
