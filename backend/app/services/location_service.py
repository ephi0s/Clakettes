from sqlalchemy.orm import Session, joinedload
from app.models.location import Location
from app.models.location_relation import LocationRelation
from app.schemas.location import LocationCreate, LocationUpdate
from .base_service import BaseService


class LocationService(BaseService[Location, LocationCreate, LocationUpdate]):
    def __init__(self):
        super().__init__(Location)

    def get_multi_paginated(
        self,
        db: Session,
        page: int = 1,
        size: int = 20,
        search: str | None = None,
        tag: str | None = None,
        is_active: bool | None = None,
        badge: str | None = None,
    ):
        query = db.query(Location)
        if search:
            like = f"%{search}%"
            query = query.filter(
                Location.name.ilike(like) | Location.description.ilike(like) | Location.address.ilike(like)
            )
        if tag:
            query = query.filter(Location.tags.any(tag))
        if is_active is not None:
            query = query.filter(Location.is_active == is_active)
        if badge:
            query = query.filter(Location.badge == badge)
        query = query.order_by(Location.name.asc())
        return self.paginate(query, page, size)

    def get_with_details(self, db: Session, location_id: int):
        return (
            db.query(Location)
            .options(
                joinedload(Location.location_tags),
                joinedload(Location.location_images),
                joinedload(Location.related_from).joinedload(LocationRelation.related_location),
                joinedload(Location.related_to).joinedload(LocationRelation.location),
                joinedload(Location.film_locations),
            )
            .filter(Location.id == location_id)
            .first()
        )
