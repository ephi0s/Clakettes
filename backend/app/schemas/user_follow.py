from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .common import PageBase


class UserFollowCreate(BaseModel):
    follower_id: int
    followed_id: int


class UserFollowResponse(BaseModel):
    id: int
    follower_id: int
    followed_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserFollowsPage(PageBase):
    items: list[UserFollowResponse]


class FollowStatus(BaseModel):
    is_following: bool
    followers_count: int
    following_count: int
