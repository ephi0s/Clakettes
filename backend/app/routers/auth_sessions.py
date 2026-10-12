from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user_session import (
    TokenRefreshRequest,
    TokenRefreshResponse,
    UserSessionResponse,
    UserSessionPage,
)
from app.auth import (
    rotate_refresh_token,
    get_current_user,
    _hash_token,
    oauth2_scheme,
)
from app.models.user import User
from app.services.auth_session_service import AuthSessionService

router = APIRouter()
auth_session_service = AuthSessionService()


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    refresh_hash = _hash_token(body.refresh_token)
    session = auth_session_service.get_by_refresh_token_hash(db, refresh_hash)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    from datetime import datetime, timezone

    if session.expires_at and session.expires_at < datetime.now(timezone.utc):
        auth_session_service.revoke_session(db, session.id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    new_access, new_refresh = rotate_refresh_token(db, session)
    return TokenRefreshResponse(access_token=new_access, refresh_token=new_refresh)


@router.get("/sessions", response_model=UserSessionPage)
async def list_sessions(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = auth_session_service.get_user_sessions_paginated(db, current_user.id, page, size)
    current_hash = _hash_token(token)
    items = []
    for s in result["items"]:
        item = UserSessionResponse.model_validate(s)
        item.is_current = s.token_hash == current_hash
        items.append(item)
    return UserSessionPage(
        items=items,
        total=result["total"],
        pages=result["pages"],
    )


@router.delete("/sessions/{session_id}", status_code=204)
async def revoke_user_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = auth_session_service.get(db, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    auth_session_service.revoke_session(db, session_id)


@router.post("/sessions/revoke-all", status_code=204)
async def revoke_all_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    auth_session_service.revoke_all_user_sessions(db, current_user.id)
