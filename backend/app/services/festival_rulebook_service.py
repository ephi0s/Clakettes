from sqlalchemy.orm import Session
from app.models.festival_rulebook import FestivalRulebook
from app.schemas.festival_rulebook import FestivalRulebookCreate, FestivalRulebookUpdate
from .base_service import BaseService


class FestivalRulebookService(BaseService[FestivalRulebook, FestivalRulebookCreate, FestivalRulebookUpdate]):
    def __init__(self):
        super().__init__(FestivalRulebook)

    def get_by_festival(
        self,
        db: Session,
        festival_id: int,
        category: str | None = None,
        event_id: int | None = None,
        published_only: bool = False,
    ) -> list[FestivalRulebook]:
        query = db.query(FestivalRulebook).filter(FestivalRulebook.festival_id == festival_id)
        if category is not None:
            query = query.filter(FestivalRulebook.category == category)
        if event_id is not None:
            query = query.filter(FestivalRulebook.event_id == event_id)
        if published_only:
            query = query.filter(FestivalRulebook.is_published.is_(True))
        return query.order_by(FestivalRulebook.created_at.desc()).all()

    def get_paginated_by_festival(
        self,
        db: Session,
        festival_id: int,
        page: int = 1,
        size: int = 20,
        category: str | None = None,
    ):
        query = db.query(FestivalRulebook).filter(FestivalRulebook.festival_id == festival_id)
        if category is not None:
            query = query.filter(FestivalRulebook.category == category)
        query = query.order_by(FestivalRulebook.created_at.desc())
        return self.paginate(query, page, size)
