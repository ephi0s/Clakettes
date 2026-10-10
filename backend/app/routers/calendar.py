"""Router for the shared agenda — a calendar spanning every visible festival.

``GET /api/calendar/agenda`` is public on purpose: visitors see public events,
and authenticated callers additionally see events addressed to them.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.dav import auth as dav_auth
from app.models.user import User
from app.routers.dependencies import get_current_user_optional
from app.routers.permissions import require_admin
from app.schemas.calendar import (
    AgendaResponse,
    CalendarSettingsPublic,
    CalendarSettingsResponse,
    CalendarSettingsUpdate,
    DavCollectionResponse,
    DavTokenResponse,
    DavTokenStatusResponse,
)
from app.services.app_setting_service import AppSettingService
from app.services.calendar_service import CalendarService
from app.services.dav_service import DavService

router = APIRouter()
calendar_service = CalendarService()
setting_service = AppSettingService()
dav_service = DavService()


@router.get("/agenda", response_model=AgendaResponse)
async def get_agenda(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    festival_ids: list[int] | None = Query(None),
    event_type: str | None = None,
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Return the agenda visible to the caller across all visible festivals."""
    return calendar_service.get_agenda(
        db,
        user=current_user,
        date_from=date_from,
        date_to=date_to,
        festival_ids=festival_ids,
        event_type=event_type,
        limit=limit,
    )


@router.get("/agenda/export/ics", response_class=PlainTextResponse)
async def export_agenda_ics(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    festival_ids: list[int] | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Download the agenda as an ICS file."""
    agenda = calendar_service.get_agenda(
        db,
        user=current_user,
        date_from=date_from,
        date_to=date_to,
        festival_ids=festival_ids,
        limit=1000,
    )
    return PlainTextResponse(
        calendar_service.export_ics(agenda),
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=agenda.ics"},
    )


@router.get("/settings", response_model=CalendarSettingsPublic)
async def get_public_settings(db: Session = Depends(get_db)):
    """Public flag telling the client whether to render the agenda at all."""
    return CalendarSettingsPublic(calendar_enabled=setting_service.is_calendar_enabled(db))


@router.get("/admin/settings", response_model=CalendarSettingsResponse)
async def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Full calendar configuration, including per-festival inclusion. Admin only."""
    require_admin(current_user)
    return calendar_service.get_settings(db)


@router.put("/admin/settings", response_model=CalendarSettingsResponse)
async def update_settings(
    body: CalendarSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle the agenda and choose which festivals appear in it. Admin only."""
    require_admin(current_user)
    return calendar_service.update_settings(
        db,
        calendar_enabled=body.calendar_enabled,
        festival_ids=body.festival_ids,
    )


def _dav_collections(db: Session, user: User) -> list[DavCollectionResponse]:
    """Collections the user may subscribe to over CalDAV."""
    return [
        DavCollectionResponse(
            name=calendar.name,
            display_name=calendar.display_name,
            description=calendar.description,
        )
        for calendar in dav_service.list_calendars(db, user)
    ]


@router.post("/dav/token", response_model=DavTokenResponse)
async def create_dav_token(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Issue a CalDAV token and return it once. Generating rotates any previous token."""
    raw = dav_auth.generate_token()
    current_user.dav_token_hash = dav_auth.hash_token(raw)
    db.commit()
    return DavTokenResponse(token=raw, collections=_dav_collections(db, current_user))


@router.get("/dav/token", response_model=DavTokenStatusResponse)
async def get_dav_token_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Report whether a CalDAV token exists. The token itself is never returned."""
    return DavTokenStatusResponse(
        has_token=bool(current_user.dav_token_hash),
        collections=_dav_collections(db, current_user),
    )


@router.delete("/dav/token", response_model=DavTokenStatusResponse)
async def revoke_dav_token(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Revoke the CalDAV token, immediately breaking every subscription."""
    current_user.dav_token_hash = None
    db.commit()
    return DavTokenStatusResponse(has_token=False, collections=_dav_collections(db, current_user))
