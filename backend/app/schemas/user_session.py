"""Pydantic schemas for user session management and refresh tokens."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserSessionBase(BaseModel):
    device_name: str = ""
    ip_address: str = ""
    user_agent: str = ""


class UserSessionCreate(UserSessionBase):
    user_id: int


class UserSessionUpdate(BaseModel):
    device_name: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    is_active: bool | None = None


class UserSessionResponse(UserSessionBase):
    id: int
    user_id: int
    last_used_at: datetime
    created_at: datetime
    expires_at: datetime
    is_active: bool
    is_current: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserSessionPage(BaseModel):
    items: list[UserSessionResponse]
    total: int
    pages: int


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class RevokeSessionRequest(BaseModel):
    reason: str | None = None


# Avoid circular imports
from app.schemas.user import UserResponse  # noqa: E402

LoginResponse.model_rebuild()
