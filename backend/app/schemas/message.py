from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .common import PageBase


class MessageBase(BaseModel):
    content: str
    sender_id: int
    receiver_id: int | None = None
    group_id: int | None = None
    channel_id: int | None = None
    message_type: str = "text"
    media_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    vcard_data: str | None = None
    ical_data: str | None = None


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    content: str | None = None
    is_read: bool | None = None
    message_type: str | None = None
    media_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    vcard_data: str | None = None
    ical_data: str | None = None
    channel_id: int | None = None


class MessageResponse(MessageBase):
    id: int
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessagesPage(PageBase):
    items: list[MessageResponse]
