from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .common import PageBase


class AuditLogCreate(BaseModel):
    actor_user_id: int | None = None
    action: str
    target_user_id: int | None = None
    detail: str | None = None
    ip_address: str | None = None


class AuditLogUpdate(BaseModel):
    pass


class AuditLogResponse(BaseModel):
    id: int
    actor_user_id: int | None = None
    action: str
    target_user_id: int | None = None
    detail: str | None = None
    ip_address: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogsPage(PageBase):
    items: list[AuditLogResponse]
