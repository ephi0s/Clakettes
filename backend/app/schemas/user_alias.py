from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .common import PageBase
from app.enums import AliasContext, AliasVisibility


class UserAliasBase(BaseModel):
    user_id: int
    alias: str
    context: str = AliasContext.GLOBAL.value
    context_id: int | None = None
    is_primary: bool = False
    is_public: bool = True
    show_awards: bool = False
    profile_token: str | None = None
    visibility_scope: str = AliasVisibility.FESTIVAL_ONLY.value
    notes: str | None = None


class UserAliasCreate(UserAliasBase):
    pass


class UserAliasUpdate(BaseModel):
    alias: str | None = None
    context: str | None = None
    context_id: int | None = None
    is_primary: bool | None = None
    is_public: bool | None = None
    show_awards: bool | None = None
    visibility_scope: str | None = None
    notes: str | None = None


class UserAliasResponse(UserAliasBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserAliasesPage(PageBase):
    items: list[UserAliasResponse]
