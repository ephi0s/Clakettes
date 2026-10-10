from sqlalchemy.orm import Session
from app.models.location_tag import LocationTag
from app.schemas.location_tag import LocationTagCreate
from .base_service import BaseService


class LocationTagService(BaseService[LocationTag, LocationTagCreate, LocationTagCreate]):
    def __init__(self):
        super().__init__(LocationTag)

    def get_by_location(self, db: Session, location_id: int) -> list[LocationTag]:
        return (
            db.query(LocationTag)
            .filter(LocationTag.location_id == location_id, LocationTag.status != "revoked")
            .order_by(LocationTag.created_at.desc())
            .all()
        )

    def create_tag(
        self, db: Session, location_id: int, tag_data: LocationTagCreate, user_id: int, is_admin: bool = False
    ) -> LocationTag:
        status = "approved" if is_admin else "proposed"
        db_obj = LocationTag(
            location_id=location_id,
            tag=tag_data.tag,
            proposed_by=user_id,
            status=status,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def revoke_tag(self, db: Session, tag_id: int) -> LocationTag | None:
        tag = self.get(db, tag_id)
        if not tag:
            return None
        tag.status = "revoked"
        db.commit()
        db.refresh(tag)
        return tag

    def approve_tag(self, db: Session, tag_id: int) -> LocationTag | None:
        tag = self.get(db, tag_id)
        if not tag:
            return None
        tag.status = "approved"
        db.commit()
        db.refresh(tag)
        return tag
