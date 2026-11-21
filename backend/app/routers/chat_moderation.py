"""Chat moderation endpoints scoped under /api/chat/moderation."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.user import User as UserModel
from app.routers.permissions import require_admin
from app.services.chat_moderation_service import ChatModerationService
from app.services.chat_rate_limit_service import chat_rate_limit

router = APIRouter(prefix="/api/chat/moderation")
service = ChatModerationService()


def _report_out(report) -> dict:
    return {
        "id": report.id,
        "reporter_id": report.reporter_id,
        "message_id": report.message_id,
        "reason": report.reason,
        "status": report.status,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


def _mute_out(mute) -> dict:
    return {
        "id": mute.id,
        "user_id": mute.user_id,
        "channel_id": mute.channel_id,
        "node_domain": mute.node_domain,
        "until": mute.until.isoformat() if mute.until else None,
        "reason": mute.reason,
    }


@router.post("/messages/{message_id}/report", status_code=201)
async def report_message(
    message_id: int,
    reason: str = Query(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return _report_out(service.report_message(db, current_user.id, message_id, reason))


@router.patch("/messages/{message_id}/moderate")
async def moderate_message(
    message_id: int,
    action: str = Query("hide"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service.moderate_message(db, message_id, action, current_user)


@router.get("/reports")
async def list_reports(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    require_admin(current_user, db)
    return [_report_out(report) for report in service.list_reports(db, status=status)]


@router.post("/mutes", status_code=201)
async def mute_user(
    user_id: int = Query(...),
    channel_id: int | None = None,
    node_domain: str | None = None,
    duration_seconds: int = Query(3600, ge=1),
    reason: str | None = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    mute = service.mute_user(
        db,
        user_id,
        current_user,
        channel_id=channel_id,
        node_domain=node_domain,
        duration_seconds=duration_seconds,
        reason=reason,
    )
    return _mute_out(mute)


@router.get("/mutes")
async def list_mutes(
    include_expired: bool = False,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    require_admin(current_user, db)
    return [_mute_out(mute) for mute in service.list_mutes(db, include_expired=include_expired)]


@router.get("/limits")
async def list_limits(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    require_admin(current_user, db)
    return {
        "max_messages": chat_rate_limit.max_messages,
        "window_seconds": chat_rate_limit.window_seconds,
        "entries": chat_rate_limit.snapshot(),
    }
