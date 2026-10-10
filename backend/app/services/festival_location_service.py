"""Service for linking locations to festivals."""

from sqlalchemy.orm import Session
from app.services.base_service import BaseService
from app.models.festival_location import FestivalLocation
from app.models.location import Location
from app.schemas.festival_location import FestivalLocationCreate


class FestivalLocationService(BaseService[FestivalLocation, FestivalLocationCreate, None]):
    def __init__(self):
        super().__init__(FestivalLocation)

    def get_locations_by_festival(self, db: Session, festival_id: int) -> list[Location]:
        return (
            db.query(Location)
            .join(FestivalLocation, FestivalLocation.location_id == Location.id)
            .filter(FestivalLocation.festival_id == festival_id)
            .order_by(Location.name.asc())
            .all()
        )

    def link(self, db: Session, festival_id: int, location_id: int) -> FestivalLocation:
        existing = (
            db.query(FestivalLocation)
            .filter(
                FestivalLocation.festival_id == festival_id,
                FestivalLocation.location_id == location_id,
            )
            .first()
        )
        if existing:
            raise ValueError("Location already linked to this festival")
        db_obj = FestivalLocation(festival_id=festival_id, location_id=location_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def unlink(self, db: Session, festival_id: int, location_id: int) -> bool:
        link = (
            db.query(FestivalLocation)
            .filter(
                FestivalLocation.festival_id == festival_id,
                FestivalLocation.location_id == location_id,
            )
            .first()
        )
        if not link:
            return False
        db.delete(link)
        db.commit()
        return True
