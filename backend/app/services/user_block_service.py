"""Service for user blocking (RGPD / safety)."""

from sqlalchemy.orm import Session
from app.models.user_block import UserBlock
from app.schemas.user_block import UserBlockCreate
from .base_service import BaseService


class UserBlockService(BaseService[UserBlock, UserBlockCreate, UserBlockCreate]):
    def __init__(self):
        super().__init__(UserBlock)

    def block(self, db: Session, blocker_id: int, blocked_id: int, reason: str | None = None) -> UserBlock:
        existing = self.get_by_pair(db, blocker_id, blocked_id)
        if existing:
            return existing
        obj = UserBlock(blocker_id=blocker_id, blocked_id=blocked_id, reason=reason)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def unblock(self, db: Session, blocker_id: int, blocked_id: int) -> bool:
        existing = self.get_by_pair(db, blocker_id, blocked_id)
        if not existing:
            return False
        db.delete(existing)
        db.commit()
        return True

    def get_by_pair(self, db: Session, blocker_id: int, blocked_id: int) -> UserBlock | None:
        return (
            db.query(UserBlock).filter(UserBlock.blocker_id == blocker_id, UserBlock.blocked_id == blocked_id).first()
        )

    def is_blocked(self, db: Session, blocker_id: int, blocked_id: int) -> bool:
        return self.get_by_pair(db, blocker_id, blocked_id) is not None

    def list_blocked(self, db: Session, blocker_id: int, page: int = 1, size: int = 20) -> dict:
        query = db.query(UserBlock).filter(UserBlock.blocker_id == blocker_id)
        return self.paginate(query.order_by(UserBlock.created_at.desc()), page, size)

    def list_blockers_of(self, db: Session, blocked_id: int) -> list[int]:
        return [r.blocker_id for r in db.query(UserBlock).filter(UserBlock.blocked_id == blocked_id).all()]
