from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .common import PageBase


class UserBlockCreate(BaseModel):
    blocked_id: int
    reason: str | None = None


class UserBlockResponse(BaseModel):
    id: int
    blocker_id: int
    blocked_id: int
    reason: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBlocksPage(PageBase):
    items: list[UserBlockResponse]
