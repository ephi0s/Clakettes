"""Award service — business logic for awards and prizes."""

from sqlalchemy.orm import Session

from app.models.award import Award
from app.schemas.award import AwardCreate, AwardUpdate
from .base_service import BaseService


class AwardService(BaseService[Award, AwardCreate, AwardUpdate]):
    def __init__(self):
        super().__init__(Award)

    def create(self, db: Session, obj_in: AwardCreate, **extra_fields) -> Award:
        data = obj_in.model_dump()
        data.update(extra_fields)
        db_obj = Award(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_festival(
        self,
        db: Session,
        festival_id: int,
        user_id: int | None = None,
        shortfilm_id: int | None = None,
        is_public: bool | None = None,
    ) -> list[Award]:
        query = db.query(Award).filter(Award.festival_id == festival_id)
        if user_id is not None:
            query = query.filter(Award.user_id == user_id)
        if shortfilm_id is not None:
            query = query.filter(Award.shortfilm_id == shortfilm_id)
        if is_public is not None:
            query = query.filter(Award.is_public == is_public)
        return query.order_by(Award.position, Award.award_name).all()

    def get_by_festivals(
        self,
        db: Session,
        festival_ids: list[int],
        user_id: int | None = None,
        shortfilm_id: int | None = None,
        is_public: bool | None = None,
    ) -> list[Award]:
        if not festival_ids:
            return []
        query = db.query(Award).filter(Award.festival_id.in_(festival_ids))
        if user_id is not None:
            query = query.filter(Award.user_id == user_id)
        if shortfilm_id is not None:
            query = query.filter(Award.shortfilm_id == shortfilm_id)
        if is_public is not None:
            query = query.filter(Award.is_public == is_public)
        return query.order_by(Award.festival_id, Award.position, Award.award_name).all()

    def get_by_festival_paginated(
        self,
        db: Session,
        festival_id: int,
        page: int,
        size: int,
        user_id: int | None = None,
        shortfilm_id: int | None = None,
        is_public: bool | None = None,
        eligibility_tag: str | None = None,
        recipient_verified: bool | None = None,
    ) -> dict:
        query = db.query(Award).filter(Award.festival_id == festival_id)
        if user_id is not None:
            query = query.filter(Award.user_id == user_id)
        if shortfilm_id is not None:
            query = query.filter(Award.shortfilm_id == shortfilm_id)
        if is_public is not None:
            query = query.filter(Award.is_public == is_public)
        if recipient_verified is not None:
            query = query.filter(Award.recipient_verified == recipient_verified)
        if eligibility_tag:
            query = query.filter(Award.eligibility_criteria.contains(eligibility_tag))
        return self.paginate(query.order_by(Award.position, Award.award_name), page, size)

    def get_by_user(
        self,
        db: Session,
        user_id: int,
        is_public: bool | None = None,
    ) -> list[Award]:
        query = db.query(Award).filter(Award.user_id == user_id)
        if is_public is not None:
            query = query.filter(Award.is_public == is_public)
        return query.order_by(Award.year.desc(), Award.festival_id).all()

    def get_by_user_paginated(
        self,
        db: Session,
        user_id: int,
        page: int,
        size: int,
        is_public: bool | None = None,
    ) -> dict:
        query = db.query(Award).filter(Award.user_id == user_id)
        if is_public is not None:
            query = query.filter(Award.is_public == is_public)
        return self.paginate(query.order_by(Award.year.desc(), Award.festival_id), page, size)

    def update_with_verification(
        self,
        db: Session,
        id: int,
        obj_in: AwardUpdate,
        verifier_id: int,
    ) -> Award | None:
        db_obj = self.get(db, id)
        if not db_obj:
            return None
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db_obj.verified_by = verifier_id
        if "is_verified" not in update_data:
            db_obj.is_verified = True
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def verify_recipient(
        self,
        db: Session,
        award: Award,
        verified: bool,
        notes: str | None,
        verifier_id: int,
    ) -> Award:
        from datetime import datetime, timezone

        award.recipient_verified = verified
        award.recipient_verification_notes = notes
        award.recipient_verified_by = verifier_id
        award.recipient_verified_at = datetime.now(timezone.utc) if verified else None
        db.commit()
        db.refresh(award)
        return award
