from sqlalchemy.orm import Session
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate
from .base_service import BaseService


class PostService(BaseService[Post, PostCreate, PostUpdate]):
    def __init__(self):
        super().__init__(Post)

    def _visible_query(self, db: Session, include_hidden: bool = False):
        query = db.query(Post)
        if not include_hidden:
            query = query.filter(Post.is_hidden.is_(False))
        return query

    def list_user_wall(self, db: Session, user_id: int, page: int = 1, size: int = 20, include_hidden: bool = False):
        query = (
            self._visible_query(db, include_hidden)
            .filter(Post.target_user_id == user_id, Post.parent_post_id.is_(None))
            .order_by(Post.is_pinned.desc(), Post.id.desc())
        )
        return self.paginate(query, page, size)

    def list_festival_wall(
        self, db: Session, festival_id: int, page: int = 1, size: int = 20, include_hidden: bool = False
    ):
        query = (
            self._visible_query(db, include_hidden)
            .filter(Post.festival_id == festival_id, Post.parent_post_id.is_(None))
            .order_by(Post.is_pinned.desc(), Post.id.desc())
        )
        return self.paginate(query, page, size)

    def list_replies(self, db: Session, post_id: int, page: int = 1, size: int = 20, include_hidden: bool = False):
        query = self._visible_query(db, include_hidden).filter(Post.parent_post_id == post_id).order_by(Post.id.asc())
        return self.paginate(query, page, size)

    def reply_count(self, db: Session, post_id: int) -> int:
        return db.query(Post).filter(Post.parent_post_id == post_id).count()

    def create_wall_post(
        self,
        db: Session,
        obj_in: PostCreate,
        author_id: int,
        target_user_id: int | None = None,
        festival_id: int | None = None,
        parent_post_id: int | None = None,
    ) -> Post:
        data = obj_in.model_dump()
        db_obj = Post(
            **data,
            author_id=author_id,
            target_user_id=target_user_id,
            festival_id=festival_id,
            parent_post_id=parent_post_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
