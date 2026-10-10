from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .common import PageBase


class NotificationBase(BaseModel):
    user_id: int
    title: str
    message: str
    notification_type: str = "profile_update"
    related_user_id: int | None = None


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationsPage(PageBase):
    items: list[NotificationResponse]
