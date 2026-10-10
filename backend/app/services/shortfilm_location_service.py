from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.services.base_service import BaseService
from app.models.shortfilm_location import ShortFilmLocation
from app.schemas.shortfilm_location import ShortFilmLocationCreate, ShortFilmLocationUpdate


class ShortFilmLocationService(BaseService[ShortFilmLocation, ShortFilmLocationCreate, ShortFilmLocationUpdate]):
    def __init__(self):
        super().__init__(ShortFilmLocation)

    def get_by_shortfilm(self, db: Session, shortfilm_id: int) -> list[ShortFilmLocation]:
        return (
            db.query(ShortFilmLocation)
            .options(joinedload(ShortFilmLocation.location))
            .filter(ShortFilmLocation.shortfilm_id == shortfilm_id)
            .order_by(ShortFilmLocation.start_time.asc().nulls_last())
            .all()
        )

    def get_by_location(self, db: Session, location_id: int) -> list[ShortFilmLocation]:
        return db.query(ShortFilmLocation).filter(ShortFilmLocation.location_id == location_id).all()

    def create_link(
        self, db: Session, shortfilm_id: int, data: ShortFilmLocationCreate, user_id: int
    ) -> ShortFilmLocation:
        existing = (
            db.query(ShortFilmLocation)
            .filter(
                and_(
                    ShortFilmLocation.shortfilm_id == shortfilm_id,
                    ShortFilmLocation.location_id == data.location_id,
                )
            )
            .first()
        )
        if existing:
            raise ValueError("Location already linked to this film")

        obj_data = data.model_dump()
        obj_data["shortfilm_id"] = shortfilm_id
        obj_data["created_by"] = user_id
        db_obj = ShortFilmLocation(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_link(self, db: Session, sfloc_id: int, data: ShortFilmLocationUpdate) -> ShortFilmLocation | None:
        return self.update(db, sfloc_id, data)
