from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Any
from .common import PageBase

BADGE_SCOPES = {"platform", "festival"}


class BadgeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    image_url: str | None = Field(None, max_length=500)
    scope: str = Field("platform", max_length=20)
    category: str | None = Field(None, max_length=30)
    festival_id: int | None = None
    conditions: dict[str, Any] | None = None
    require_conditions: bool | None = True
    is_active: bool | None = True


class BadgeCreate(BadgeBase):
    pass


class BadgeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    image_url: str | None = Field(None, max_length=500)
    scope: str | None = Field(None, max_length=20)
    category: str | None = Field(None, max_length=30)
    festival_id: int | None = None
    conditions: dict[str, Any] | None = None
    require_conditions: bool | None = None
    is_active: bool | None = None


class BadgeResponse(BadgeBase):
    id: int
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BadgesPage(PageBase):
    items: list[BadgeResponse]


class BadgeAssignRequest(BaseModel):
    target_user_id: int | None = None
    target_festival_id: int | None = None
    grant_festival_id: int | None = None
    reason: str | None = Field(None, max_length=1000)
    force: bool = False


class BadgeAssignmentResponse(BaseModel):
    id: int
    badge_id: int
    target_user_id: int | None = None
    target_festival_id: int | None = None
    granted_by: int
    grant_festival_id: int | None = None
    reason: str | None = None
    created_at: datetime
    updated_at: datetime
    badge: BadgeResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class BadgeAssignmentsPage(PageBase):
    items: list[BadgeAssignmentResponse]


class BadgeEligibilityResponse(BaseModel):
    eligible: bool
    reason: str | None = None


class BadgeStatusResponse(BaseModel):
    enabled: bool


class BadgeSettingsUpdate(BaseModel):
    enabled: bool
