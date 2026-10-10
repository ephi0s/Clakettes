from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.location import Location
from app.models.location_image import LocationImage
from app.routers.dependencies import get_or_404
from app.schemas.location_image import LocationImageResponse
from app.services.location_image_service import LocationImageService
from app.services.location_service import LocationService
from app.routers.permissions import require_location_admin
from app.routers.uploads import _save_file, ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE

router = APIRouter()
image_service = LocationImageService()
location_service = LocationService()


class ImageUrlRequest(BaseModel):
    url: str


@router.get("/", response_model=list[LocationImageResponse])
async def list_location_images(location_id: int, db: Session = Depends(get_db)):
    return image_service.get_by_location(db, location_id)


@router.post("/upload", response_model=LocationImageResponse, status_code=201)
async def upload_location_image(
    location_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    location = get_or_404(db, Location, location_id, "Location")
    require_location_admin(db, current_user, location)
    url = await _save_file(file, "locations", ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)
    return image_service.add_upload(db, location_id, url, current_user.id)


@router.post("/url", response_model=LocationImageResponse, status_code=201)
async def add_location_image_url(
    location_id: int,
    body: ImageUrlRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    location = get_or_404(db, Location, location_id, "Location")
    require_location_admin(db, current_user, location)
    return image_service.add_url(db, location_id, body.url, current_user.id)


@router.delete("/{image_id}")
async def delete_location_image(
    location_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = get_or_404(db, LocationImage, image_id, "Image")
    location = get_or_404(db, Location, image.location_id, "Location")
    require_location_admin(db, current_user, location)
    removed = image_service.remove_image(db, image_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image removed"}
