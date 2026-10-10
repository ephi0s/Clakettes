"""Service for UserAlias."""

from sqlalchemy.orm import Session, joinedload
from app.models.user_alias import UserAlias
from app.schemas.user_alias import UserAliasCreate, UserAliasUpdate
from .base_service import BaseService


class UserAliasService(BaseService[UserAlias, UserAliasCreate, UserAliasUpdate]):
    def __init__(self):
        super().__init__(UserAlias)

    def get_by_user(self, db: Session, user_id: int, context: str | None = None) -> list:
        query = db.query(UserAlias).filter(UserAlias.user_id == user_id)
        if context:
            query = query.filter(UserAlias.context == context)
        return query.all()

    def get_by_user_paginated(
        self,
        db: Session,
        user_id: int,
        page: int,
        size: int,
        context: str | None = None,
    ) -> dict:
        query = db.query(UserAlias).filter(UserAlias.user_id == user_id)
        if context:
            query = query.filter(UserAlias.context == context)
        return self.paginate(query, page, size)

    def get_by_token(self, db: Session, token: str) -> UserAlias | None:
        return (
            db.query(UserAlias)
            .options(joinedload(UserAlias.user))
            .filter(
                UserAlias.profile_token == token,
                UserAlias.is_public,
            )
            .first()
        )

    def get_by_user_and_context(
        self,
        db: Session,
        user_id: int,
        context: str,
        context_id: int,
    ) -> UserAlias | None:
        return (
            db.query(UserAlias)
            .filter(
                UserAlias.user_id == user_id,
                UserAlias.context == context,
                UserAlias.context_id == context_id,
                UserAlias.is_public,
            )
            .first()
        )
