from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime
from .common import PageBase


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str | None = Field(None, max_length=200)
    role: str | None = Field(None, max_length=50)
    bio: str | None = Field(None, max_length=2000)
    avatar_url: str | None = Field(None, max_length=500)
    banner_url: str | None = Field(None, max_length=500)
    tagline: str | None = Field(None, max_length=200)
    social_links: dict[str, str] | None = None
    is_public: bool | None = False
    is_public_email: bool | None = False
    is_public_bio: bool | None = False
    is_public_location: bool | None = False
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    privacy_policy_version: str | None = Field(None, max_length=20)
    privacy_accepted_at: datetime | None = None


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=128)
    device_name: str | None = None


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = None
    full_name: str | None = Field(None, max_length=200)
    role: str | None = Field(None, max_length=50)
    bio: str | None = Field(None, max_length=2000)
    avatar_url: str | None = Field(None, max_length=500)
    banner_url: str | None = Field(None, max_length=500)
    tagline: str | None = Field(None, max_length=200)
    social_links: dict[str, str] | None = None
    is_public: bool | None = None
    is_public_email: bool | None = None
    is_public_bio: bool | None = None
    is_public_location: bool | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    password: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    user_roles: list["UserRoleResponse"] = []
    user_participant_tags: list["UserParticipantTagResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class UserWithRolesResponse(UserResponse):
    """User with festival-scoped roles and tags for a specific festival."""

    festival_roles: list["UserRoleResponse"] = []
    festival_tags: list["UserParticipantTagResponse"] = []


class UserPublicResponse(BaseModel):
    """Public-safe user response — only includes fields the user has made public."""

    id: int
    username: str
    full_name: str | None = None
    role: str | None = None
    avatar_url: str | None = None
    banner_url: str | None = None
    tagline: str | None = None
    social_links: dict[str, str] | None = None
    is_active: bool
    email: str | None = None
    bio: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UsersPage(PageBase):
    items: list[UserResponse]


class UsersPublicPage(PageBase):
    items: list[UserPublicResponse]


# Forward references
from .user_role import UserRoleResponse, UserParticipantTagResponse  # noqa: E402

UserResponse.model_rebuild()
UserWithRolesResponse.model_rebuild()
