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
        user_id: int | None = None,
        is_public: bool | None = None,
    ):
        query = db.query(ShortFilm)
        if festival_id:
            query = query.filter(ShortFilm.festival_id == festival_id)
        if user_id:
            query = query.filter(ShortFilm.user_id == user_id)
        if is_public is not None:
            query = query.filter(ShortFilm.is_public == is_public)
        return self.paginate(query, page, size)
