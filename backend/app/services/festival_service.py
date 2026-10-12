from sqlalchemy.orm import Session
from app.models.festival import Festival
from app.schemas.festival import FestivalCreate, FestivalUpdate
from .base_service import BaseService


class FestivalService(BaseService[Festival, FestivalCreate, FestivalUpdate]):
    def __init__(self):
        super().__init__(Festival)

    def get_multi_paginated(self, db: Session, page: int = 1, size: int = 20, is_active: bool | None = None):
        filters = []
        if is_active is not None:
            filters.append(Festival.is_active == is_active)
        return self.paginate_filtered(db, page, size, *filters)

    def get_multi_by_ids(self, db: Session, festival_ids: list[int]) -> list[Festival]:
        if not festival_ids:
            return []
        return db.query(Festival).filter(Festival.id.in_(festival_ids)).all()
