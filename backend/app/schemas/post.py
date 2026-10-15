from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from .common import PageBase

EMBED_TYPES = {"youtube", "vimeo", "dailymotion", "odysee", "ivoox", "podimo", "generic"}


class PostBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    embed_url: str | None = Field(None, max_length=1000)
    embed_type: str | None = Field(None, max_length=30)
    allow_replies: bool | None = True

    @field_validator("embed_type")
    @classmethod
    def validate_embed_type(cls, v):
        if v is not None and v not in EMBED_TYPES:
            raise ValueError(f"embed_type must be one of {sorted(EMBED_TYPES)}")
        return v


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    content: str | None = Field(None, min_length=1, max_length=5000)
    embed_url: str | None = Field(None, max_length=1000)
    embed_type: str | None = Field(None, max_length=30)
    allow_replies: bool | None = None

    @field_validator("embed_type")
    @classmethod
    def validate_embed_type(cls, v):
        if v is not None and v not in EMBED_TYPES:
            raise ValueError(f"embed_type must be one of {sorted(EMBED_TYPES)}")
        return v


class PostModerate(BaseModel):
    is_hidden: bool | None = None
    is_pinned: bool | None = None
    allow_replies: bool | None = None


class PostResponse(PostBase):
    id: int
    author_id: int
    target_user_id: int | None = None
    festival_id: int | None = None
    parent_post_id: int | None = None
    is_pinned: bool
    is_hidden: bool
    reply_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostsPage(PageBase):
    items: list[PostResponse]
