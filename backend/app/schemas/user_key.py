from pydantic import BaseModel, ConfigDict
from datetime import datetime


class UserKeyUpload(BaseModel):
    public_key_x25519: str


class UserKeyCreate(BaseModel):
    user_id: int
    public_key_x25519: str
    key_identifier: str


class UserKeyUpdate(BaseModel):
    public_key_x25519: str | None = None
    key_identifier: str | None = None
    is_active: int | None = None


class UserKeyResponse(BaseModel):
    user_id: int
    public_key_x25519: str
    key_identifier: str
    rotated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
