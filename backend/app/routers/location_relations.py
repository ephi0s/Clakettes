from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.services.location_relation_service import LocationRelationService
from app.services.location_service import LocationService
from app.models.location import Location
from app.models.location_relation import LocationRelation
from app.routers.dependencies import get_or_404
from app.schemas.location_relation import LocationRelationCreate, LocationRelationResponse
from app.routers.permissions import require_location_admin
from app.models.user import User

router = APIRouter()

service = LocationRelationService()
location_service = LocationService()


@router.get("/", response_model=list[LocationRelationResponse])
def list_related_locations(location_id: int, db: Session = Depends(get_db)):
    return service.get_related(db, location_id)


@router.post("/", response_model=LocationRelationResponse, status_code=201)
def add_relation(
    location_id: int,
    data: LocationRelationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    location = get_or_404(db, Location, location_id, "Location")
    require_location_admin(db, current_user, location)
    return service.create_relation(db, location_id, data, current_user.id)


@router.delete("/{relation_id}")
def remove_relation(
    location_id: int,
    relation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    relation = get_or_404(db, LocationRelation, relation_id, "Relation")
    location = get_or_404(db, Location, relation.location_id, "Location")
    require_location_admin(db, current_user, location)
    service.remove_relation(db, relation_id)
    return {"message": "Relation removed"}


@router.post("/suggest")
def suggest_relations(
    location_id: int,
    radius_km: float = 1.0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    proximity = service.suggest_proximity(db, location_id, radius_km)
    tags = service.suggest_by_tags(db, location_id)
    return {"proximity": proximity, "tags": tags}
