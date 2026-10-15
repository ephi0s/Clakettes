"""Router for profile badges (insignias).

Badge definitions are created by the platform admin team with an uploaded
artwork image (SVG preferred). Platform badges are granted by central admins;
festival merit badges (veteran, popular, role, special prize) are granted by
the festival's management. Everything is gated behind the ``badges.enabled``
setting, which is off by default — central admins always bypass the gate.
"""

from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.badge import Badge, BadgeAssignment
from app.models.festival import Festival
from app.models.user import User
from app.routers.dependencies import get_current_user_optional, get_or_404
from app.routers.permissions import can_manage_festival, is_admin, require_admin
from app.schemas.badge import (
    BadgeAssignRequest,
    BadgeAssignmentResponse,
    BadgeAssignmentsPage,
    BadgeCreate,
    BadgeEligibilityResponse,
    BadgeResponse,
    BadgeSettingsUpdate,
    BadgeStatusResponse,
    BadgeUpdate,
    BadgesPage,
)
from app.services.app_setting_service import BADGES_ENABLED, AppSettingService
from app.services.badge_service import BadgeService, check_eligibility

router = APIRouter()

badge_service = BadgeService()
setting_service = AppSettingService()

BADGE_DIR = Path("uploads/badges")
BADGE_MAX_SIZE = 2 * 1024 * 1024
BADGE_ALLOWED = {
    ".svg": ("image/svg+xml",),
    ".png": ("image/png",),
    ".jpg": ("image/jpeg",),
    ".jpeg": ("image/jpeg",),
    ".webp": ("image/webp",),
}


def _require_feature(db: Session, user: User | None) -> None:
    if user is not None and is_admin(user):
        return
    if setting_service.is_badges_enabled(db):
        return
    raise HTTPException(status_code=403, detail="Badges are disabled")


def _validate_conditions_shape(conditions: dict | None) -> None:
    if conditions is None:
        return
    if conditions.get("type") not in {"manual", "veteran", "role", "award", "popular"}:
        raise HTTPException(status_code=422, detail="Unknown condition type")


def _check_svg(data: bytes) -> bool:
    head = data[:1024].lstrip().lower()
    return b"<svg" in head


def _check_raster(data: bytes, ext: str) -> bool:
    if ext == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if ext in {".jpg", ".jpeg"}:
        return data.startswith(b"\xff\xd8\xff")
    if ext == ".webp":
        return data.startswith(b"RIFF") and data[8:12] == b"WEBP"
    return False


@router.get("/badges/status", response_model=BadgeStatusResponse)
async def badge_status(db: Session = Depends(get_db)):
    return {"enabled": setting_service.is_badges_enabled(db)}


@router.put("/badges/settings", response_model=BadgeStatusResponse)
async def update_badge_settings(
    settings: BadgeSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    setting_service.set_value(db, BADGES_ENABLED, settings.enabled, "Profile badges feature flag")
    return {"enabled": settings.enabled}


@router.get("/badges/", response_model=BadgesPage)
async def list_badges(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    scope: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    _require_feature(db, current_user)
    return badge_service.list_active(db, page, size, scope)


@router.post("/badges/", response_model=BadgeResponse, status_code=201)
async def create_badge(
    badge: BadgeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    _validate_conditions_shape(badge.conditions)
    if badge.scope == "festival" and badge.festival_id is not None:
        get_or_404(db, Festival, badge.festival_id, "Festival")
    created = badge_service.create(db, badge)
    created.created_by = current_user.id
    db.commit()
    db.refresh(created)
    return created


@router.get("/badges/{badge_id}", response_model=BadgeResponse)
async def get_badge(
    badge_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    _require_feature(db, current_user)
    return get_or_404(db, Badge, badge_id, "Badge")


@router.put("/badges/{badge_id}", response_model=BadgeResponse)
async def update_badge(
    badge_id: int,
    badge: BadgeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    get_or_404(db, Badge, badge_id, "Badge")
    if badge.conditions is not None:
        _validate_conditions_shape(badge.conditions)
    return badge_service.update(db, badge_id, badge)


@router.delete("/badges/{badge_id}")
async def delete_badge(
    badge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    get_or_404(db, Badge, badge_id, "Badge")
    badge_service.delete(db, badge_id)
    return {"message": "Badge deleted"}


@router.post("/badges/{badge_id}/image", response_model=BadgeResponse)
async def upload_badge_image(
    badge_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    badge = get_or_404(db, Badge, badge_id, "Badge")
    ext = Path(file.filename or "").suffix.lower()
    if ext not in BADGE_ALLOWED:
        raise HTTPException(status_code=400, detail="Image must be SVG (preferred), PNG, JPG or WebP")
    data = await file.read()
    if not data or len(data) > BADGE_MAX_SIZE:
        raise HTTPException(status_code=413, detail="Image too large (max 2 MB)")
    valid = _check_svg(data) if ext == ".svg" else _check_raster(data, ext)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid image content")
    BADGE_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    (BADGE_DIR / filename).write_bytes(data)
    badge.image_url = f"/uploads/badges/{filename}"
    db.commit()
    db.refresh(badge)
    return badge


@router.get("/badges/{badge_id}/eligibility", response_model=BadgeEligibilityResponse)
async def badge_eligibility(
    badge_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    _require_feature(db, current_user)
    badge = get_or_404(db, Badge, badge_id, "Badge")
    get_or_404(db, User, user_id, "User")
    eligible, reason = check_eligibility(db, badge, user_id)
    return {"eligible": eligible, "reason": reason}


@router.post("/badges/{badge_id}/assign", response_model=BadgeAssignmentResponse, status_code=201)
async def assign_badge(
    badge_id: int,
    payload: BadgeAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_feature(db, current_user)
    badge = get_or_404(db, Badge, badge_id, "Badge")
    if not badge.is_active:
        raise HTTPException(status_code=422, detail="Badge is not active")
    targets = [payload.target_user_id is not None, payload.target_festival_id is not None]
    if sum(targets) != 1:
        raise HTTPException(status_code=422, detail="Exactly one target (user or festival) is required")
    if payload.target_user_id is not None:
        get_or_404(db, User, payload.target_user_id, "User")
    if payload.target_festival_id is not None:
        get_or_404(db, Festival, payload.target_festival_id, "Festival")

    if badge.scope == "platform":
        require_admin(current_user)
        grant_festival_id = None
    else:
        grant_festival_id = badge.festival_id or payload.grant_festival_id
        if grant_festival_id is None:
            raise HTTPException(status_code=422, detail="grant_festival_id is required for festival badges")
        get_or_404(db, Festival, grant_festival_id, "Festival")
        if not (is_admin(current_user) or can_manage_festival(db, current_user, grant_festival_id)):
            raise HTTPException(status_code=403, detail="Only the festival management can grant this badge")

    if badge.require_conditions and payload.target_user_id is not None:
        eligible, reason = check_eligibility(db, badge, payload.target_user_id)
        if not eligible and not (payload.force and is_admin(current_user)):
            raise HTTPException(status_code=422, detail=f"Conditions not met: {reason}")

    return badge_service.grant(
        db,
        badge,
        granted_by=current_user.id,
        target_user_id=payload.target_user_id,
        target_festival_id=payload.target_festival_id,
        grant_festival_id=grant_festival_id,
        reason=payload.reason,
    )


@router.delete("/badge-assignments/{assignment_id}")
async def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_feature(db, current_user)
    assignment = get_or_404(db, BadgeAssignment, assignment_id, "BadgeAssignment")
    allowed = is_admin(current_user)
    if not allowed and assignment.grant_festival_id is not None:
        allowed = can_manage_festival(db, current_user, assignment.grant_festival_id)
    if not allowed:
        raise HTTPException(status_code=403, detail="Not allowed to remove this badge")
    db.delete(assignment)
    db.commit()
    return {"message": "Badge assignment deleted"}


@router.get("/users/{user_id}/badges/", response_model=BadgeAssignmentsPage)
async def list_user_badges(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    _require_feature(db, current_user)
    get_or_404(db, User, user_id, "User")
    return badge_service.list_assignments_for_user(db, user_id, page, size)


@router.get("/festivals/{festival_id}/badges/", response_model=BadgeAssignmentsPage)
async def list_festival_badges(
    festival_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    _require_feature(db, current_user)
    get_or_404(db, Festival, festival_id, "Festival")
    return badge_service.list_assignments_for_festival(db, festival_id, page, size)
