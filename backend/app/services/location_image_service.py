from sqlalchemy.orm import Session
from app.models.location_image import LocationImage
from app.schemas.location_image import LocationImageAdd
from .base_service import BaseService


class LocationImageService(BaseService[LocationImage, LocationImageAdd, LocationImageAdd]):
    def __init__(self):
        super().__init__(LocationImage)

    def get_by_location(self, db: Session, location_id: int) -> list[LocationImage]:
        return (
            db.query(LocationImage)
            .filter(LocationImage.location_id == location_id)
            .order_by(LocationImage.created_at.desc())
            .all()
        )

    def add_upload(self, db: Session, location_id: int, url: str, user_id: int) -> LocationImage:
        obj = LocationImage(
            location_id=location_id,
            url=url,
            source="upload",
            added_by=user_id,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def add_url(self, db: Session, location_id: int, url: str, user_id: int) -> LocationImage:
        obj = LocationImage(
            location_id=location_id,
            url=url,
            source="url",
            added_by=user_id,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def remove_image(self, db: Session, image_id: int) -> LocationImage | None:
        obj = self.get(db, image_id)
        if not obj:
            return None
        db.delete(obj)
        db.commit()
        return obj
