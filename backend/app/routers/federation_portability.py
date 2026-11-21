from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.routers.permissions import require_admin
from app.services.portability_service import PortabilityService

router = APIRouter(prefix="/api/federation/portability", tags=["federation-portability"])
service = PortabilityService()


def _admin_user(current_user: User = Depends(get_current_user)) -> User:
    require_admin(current_user)
    return current_user


class BundleIn(BaseModel):
    bundle_version: str
    created_at: str | None = None
    origin_domain: str | None = None
    payload: dict
    signature: str
    checksum: str


@router.post("/bundles")
async def create_bundle(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.create_bundle(db, current_user)


@router.post("/imports")
async def import_bundle(
    bundle: BundleIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.import_bundle(db, bundle.model_dump())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid bundle: integrity check failed")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Origin node not allowed")


@router.post("/festivals/{festival_id}/migrate")
async def migrate_festival(
    festival_id: int,
    target_domain: str = Query(...),
    new_owner_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
):
    try:
        return service.migrate_festival(db, festival_id, target_domain, new_owner_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/users/{user_ref}/migrate")
async def migrate_user(
    user_ref: str,
    target_domain: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
):
    try:
        return service.migrate_user(db, user_ref, target_domain)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/redirects/{old_ref}")
async def get_redirect(old_ref: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    redirect = service.get_redirect(db, old_ref)
    if redirect is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Redirect not found")
    return redirect
