"""Service for user follows (social graph)."""

from sqlalchemy.orm import Session

from app.models.user_follow import UserFollow
from app.schemas.user_follow import UserFollowCreate

from .base_service import BaseService


class UserFollowService(BaseService[UserFollow, UserFollowCreate, UserFollowCreate]):
    def __init__(self):
        super().__init__(UserFollow)

    def get_by_pair(self, db: Session, follower_id: int, followed_id: int) -> UserFollow | None:
        return (
            db.query(UserFollow)
            .filter(UserFollow.follower_id == follower_id, UserFollow.followed_id == followed_id)
            .first()
        )

    def follow(self, db: Session, follower_id: int, followed_id: int) -> UserFollow:
        existing = self.get_by_pair(db, follower_id, followed_id)
        if existing:
            return existing
        obj = UserFollow(follower_id=follower_id, followed_id=followed_id)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def unfollow(self, db: Session, follower_id: int, followed_id: int) -> bool:
        existing = self.get_by_pair(db, follower_id, followed_id)
        if not existing:
            return False
        db.delete(existing)
        db.commit()
        return True

    def is_following(self, db: Session, follower_id: int, followed_id: int) -> bool:
        return self.get_by_pair(db, follower_id, followed_id) is not None

    def count_followers(self, db: Session, user_id: int) -> int:
        return db.query(UserFollow).filter(UserFollow.followed_id == user_id).count()

    def count_following(self, db: Session, user_id: int) -> int:
        return db.query(UserFollow).filter(UserFollow.follower_id == user_id).count()

    def status(self, db: Session, user_id: int, viewer_id: int) -> dict:
        return {
            "is_following": self.is_following(db, viewer_id, user_id),
            "followers_count": self.count_followers(db, user_id),
            "following_count": self.count_following(db, user_id),
        }

    def list_followers(self, db: Session, user_id: int, page: int = 1, size: int = 20) -> dict:
        query = db.query(UserFollow).filter(UserFollow.followed_id == user_id)
        return self.paginate(query.order_by(UserFollow.created_at.desc()), page, size)

    def list_following(self, db: Session, user_id: int, page: int = 1, size: int = 20) -> dict:
        query = db.query(UserFollow).filter(UserFollow.follower_id == user_id)
        return self.paginate(query.order_by(UserFollow.created_at.desc()), page, size)
