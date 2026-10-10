import hashlib
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.user_key import UserKey
from app.schemas.user_key import UserKeyCreate, UserKeyUpdate, UserKeyUpload
from .base_service import BaseService


class UserKeyService(BaseService[UserKey, UserKeyCreate, UserKeyUpdate]):
    def __init__(self):
        super().__init__(UserKey)

    def get_by_user(self, db: Session, user_id: int) -> UserKey | None:
        return (
            db.query(UserKey)
            .filter(
                UserKey.user_id == user_id,
                UserKey.is_active == 1,
            )
            .first()
        )

    def set_or_update_public_key(self, db: Session, user_id: int, key_data: UserKeyUpload) -> UserKey:
        fingerprint = hashlib.sha256(key_data.public_key_x25519.encode()).hexdigest()[:16]
        existing = self.get_by_user(db, user_id)
        if existing:
            existing.public_key_x25519 = key_data.public_key_x25519
            existing.key_identifier = fingerprint
            existing.is_active = 1
            existing.rotated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            return existing
        key_entry = UserKey(
            user_id=user_id,
            public_key_x25519=key_data.public_key_x25519,
            key_identifier=fingerprint,
        )
        db.add(key_entry)
        db.commit()
        db.refresh(key_entry)
        return key_entry
