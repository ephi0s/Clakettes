"""Services for ParticipantTag, FestivalParticipantTag, and UserParticipantTag."""

from sqlalchemy.orm import Session, joinedload
from app.models.participant_tag import ParticipantTag, FestivalParticipantTag
from app.models.user_role import UserParticipantTag
from app.schemas.participant_tag import (
    ParticipantTagCreate,
    ParticipantTagUpdate,
    FestivalParticipantTagCreate,
    FestivalParticipantTagUpdate,
)
from app.schemas.user_role import UserParticipantTagCreate, UserParticipantTagUpdate
from .base_service import BaseService


class ParticipantTagService(BaseService[ParticipantTag, ParticipantTagCreate, ParticipantTagUpdate]):
    def __init__(self):
        super().__init__(ParticipantTag)

    def get_all(self, db: Session, category: str | None = None) -> list:
        query = db.query(ParticipantTag)
        if category:
            query = query.filter(ParticipantTag.category == category)
        return query.order_by(ParticipantTag.sort_order).all()

    def get_all_paginated(self, db: Session, page: int, size: int, category: str | None = None) -> dict:
        filters = []
        if category:
            filters.append(ParticipantTag.category == category)
        return self.paginate_filtered(db, page, size, *filters, order_by=ParticipantTag.sort_order)

    def get_by_name(self, db: Session, name: str):
        return db.query(ParticipantTag).filter(ParticipantTag.name == name).first()


class FestivalParticipantTagService(
    BaseService[FestivalParticipantTag, FestivalParticipantTagCreate, FestivalParticipantTagUpdate]
):
    def __init__(self):
        super().__init__(FestivalParticipantTag)

    def get_by_festival(self, db: Session, festival_id: int) -> list:
        return (
            db.query(FestivalParticipantTag)
            .filter(FestivalParticipantTag.festival_id == festival_id)
            .options(joinedload(FestivalParticipantTag.tag))
            .all()
        )

    def get_by_festival_paginated(self, db: Session, festival_id: int, page: int, size: int) -> dict:
        query = db.query(FestivalParticipantTag).filter(FestivalParticipantTag.festival_id == festival_id)
        return self.paginate(query.options(joinedload(FestivalParticipantTag.tag)), page, size)

    def get_by_festival_and_tag(self, db: Session, festival_id: int, tag_id: int):
        return (
            db.query(FestivalParticipantTag)
            .filter(
                FestivalParticipantTag.festival_id == festival_id,
                FestivalParticipantTag.tag_id == tag_id,
            )
            .first()
        )


class UserParticipantTagService(BaseService[UserParticipantTag, UserParticipantTagCreate, UserParticipantTagUpdate]):
    def __init__(self):
        super().__init__(UserParticipantTag)

    def get_by_user(self, db: Session, user_id: int, festival_id: int | None = None) -> list:
        query = db.query(UserParticipantTag).filter(UserParticipantTag.user_id == user_id)
        if festival_id:
            query = query.filter(UserParticipantTag.festival_id == festival_id)
        return query.options(joinedload(UserParticipantTag.tag)).all()

    def get_by_user_in_festivals(self, db: Session, user_id: int, festival_ids: list[int]) -> list:
        if not festival_ids:
            return []
        query = db.query(UserParticipantTag).filter(
            UserParticipantTag.user_id == user_id, UserParticipantTag.festival_id.in_(festival_ids)
        )
        return (
            query.options(joinedload(UserParticipantTag.tag))
            .order_by(UserParticipantTag.festival_id, UserParticipantTag.id)
            .all()
        )

    def get_by_user_paginated(
        self,
        db: Session,
        user_id: int,
        page: int,
        size: int,
        festival_id: int | None = None,
    ) -> dict:
        query = db.query(UserParticipantTag).filter(UserParticipantTag.user_id == user_id)
        if festival_id:
            query = query.filter(UserParticipantTag.festival_id == festival_id)
        return self.paginate(query.options(joinedload(UserParticipantTag.tag)), page, size)

    def get_by_user_and_tag(self, db: Session, user_id: int, tag_id: int, festival_id: int | None = None):
        return (
            db.query(UserParticipantTag)
            .filter(
                UserParticipantTag.user_id == user_id,
                UserParticipantTag.tag_id == tag_id,
                UserParticipantTag.festival_id == festival_id,
            )
            .first()
        )
