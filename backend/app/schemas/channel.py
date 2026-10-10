from typing import Literal
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .common import PageBase

ChannelMemberRole = Literal["admin", "moderator", "member"]


class ChannelBase(BaseModel):
    name: str
    description: str | None = None
    channel_type: str = "community"
    max_members: int | None = None


class ChannelCreate(ChannelBase):
    pass


class ChannelUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    channel_type: str | None = None
    max_members: int | None = None
    is_active: bool | None = None


class ChannelMemberBase(BaseModel):
    channel_id: int
    user_id: int
    role: str = "member"


class ChannelMemberCreate(BaseModel):
    user_id: int
    role: ChannelMemberRole = "member"


class ChannelMemberUpdate(BaseModel):
    role: ChannelMemberRole | None = None
    is_active: bool | None = None


class ChannelMemberResponse(ChannelMemberBase):
    id: int
    joined_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ChannelResponse(ChannelBase):
    id: int
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    members: list[ChannelMemberResponse] | None = None

    model_config = ConfigDict(from_attributes=True)


class ChannelsPage(PageBase):
    items: list[ChannelResponse]
