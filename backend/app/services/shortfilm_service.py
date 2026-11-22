from sqlalchemy.orm import Session
from app.models.shortfilm import ShortFilm
from app.schemas.shortfilm import ShortFilmCreate, ShortFilmUpdate
from .base_service import BaseService


class ShortFilmService(BaseService[ShortFilm, ShortFilmCreate, ShortFilmUpdate]):
    def __init__(self):
        super().__init__(ShortFilm)

    def get_multi_paginated(
        self,
        db: Session,
        page: int = 1,
        size: int = 20,
        festival_id: int | None = None,
        contest_type: str | None = None,
        user_id: int | None = None,
        is_public: bool | None = None,
    ):
        filters = []
        if festival_id:
            filters.append(ShortFilm.festival_id == festival_id)
        if contest_type:
            filters.append(ShortFilm.contest_type == contest_type)
        if user_id:
            filters.append(ShortFilm.user_id == user_id)
        if is_public is not None:
            filters.append(ShortFilm.is_public == is_public)
        return self.paginate_filtered(db, page, size, *filters)
