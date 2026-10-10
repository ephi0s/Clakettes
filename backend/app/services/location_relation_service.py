import math
from sqlalchemy.orm import Session, joinedload
from app.models.location_relation import LocationRelation
from app.models.location import Location
from app.schemas.location_relation import LocationRelationCreate
from .base_service import BaseService


class LocationRelationService(BaseService[LocationRelation, LocationRelationCreate, LocationRelationCreate]):
    def __init__(self):
        super().__init__(LocationRelation)

    def get_related(self, db: Session, location_id: int) -> list[LocationRelation]:
        return (
            db.query(LocationRelation)
            .filter(LocationRelation.location_id == location_id)
            .options(joinedload(LocationRelation.related_location))
            .all()
        )

    def create_relation(
        self, db: Session, location_id: int, data: LocationRelationCreate, user_id: int | None = None
    ) -> LocationRelation:
        existing = (
            db.query(LocationRelation)
            .filter(
                LocationRelation.location_id == location_id,
                LocationRelation.related_location_id == data.related_location_id,
            )
            .first()
        )
        if existing:
            raise ValueError("Relation already exists")
        db_obj = LocationRelation(
            location_id=location_id,
            related_location_id=data.related_location_id,
            relation_type=data.relation_type,
            suggested_by=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_relation(self, db: Session, relation_id: int) -> LocationRelation | None:
        obj = self.get(db, relation_id)
        if not obj:
            return None
        db.delete(obj)
        db.commit()
        return obj

    def suggest_proximity(self, db: Session, location_id: int, radius_km: float = 1.0) -> list[LocationRelation]:
        origin = db.query(Location).filter(Location.id == location_id).first()
        if not origin:
            return []
        R = 6371
        lat1 = math.radians(origin.latitude)
        lon1 = math.radians(origin.longitude)

        related_ids = [
            r.related_location_id
            for r in db.query(LocationRelation).filter(LocationRelation.location_id == location_id).all()
        ]

        candidates = db.query(Location).filter(Location.id != location_id, Location.is_active).all()
        created = []
        for loc in candidates:
            if loc.id in related_ids:
                continue
            lat2 = math.radians(loc.latitude)
            lon2 = math.radians(loc.longitude)
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c
            if distance <= radius_km:
                db_obj = LocationRelation(
                    location_id=location_id,
                    related_location_id=loc.id,
                    relation_type="proximity",
                    suggested_by=None,
                )
                db.add(db_obj)
                db.flush()
                db.refresh(db_obj)
                created.append(db_obj)
        db.commit()
        return created

    def suggest_by_tags(self, db: Session, location_id: int) -> list[LocationRelation]:
        origin = db.query(Location).filter(Location.id == location_id).first()
        if not origin or not origin.tags:
            return []

        related_ids = [
            r.related_location_id
            for r in db.query(LocationRelation).filter(LocationRelation.location_id == location_id).all()
        ]

        candidates = (
            db.query(Location).filter(Location.id != location_id, Location.is_active, Location.tags.isnot(None)).all()
        )

        origin_tags = set(origin.tags) if isinstance(origin.tags, list) else set()

        created = []
        for loc in candidates:
            if loc.id in related_ids:
                continue
            loc_tags = set(loc.tags) if isinstance(loc.tags, list) else set()
            if origin_tags & loc_tags:
                db_obj = LocationRelation(
                    location_id=location_id,
                    related_location_id=loc.id,
                    relation_type="tags",
                    suggested_by=None,
                )
                db.add(db_obj)
                db.flush()
                db.refresh(db_obj)
                created.append(db_obj)
        db.commit()
        return created
