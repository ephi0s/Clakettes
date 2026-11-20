"""Shared router helpers and dependencies."""

from typing import Type

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth import get_user_with_roles, validate_access_token
from app.database import get_db
from app.models.user import User
from app.services.auth_session_service import touch_session

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/users/login", auto_error=False)


def get_or_404(db: Session, model: Type, id: int, label: str = "Resource"):
    """Fetch ``model`` by id or raise 404. Replaces ~100 inline HTTPException blocks."""
    obj = db.query(model).filter(model.id == id).first()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{label} not found")
    return obj


async def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> User | None:
    """Return the current user, or None when the token is missing or invalid (no 401).

    Reuses app.auth.validate_access_token so JWT/session rules live in one place.
    """
    if not token:
        return None
    result = validate_access_token(db, token)
    if result is None:
        return None
    user_id, session = result

    touch_session(db, session)
    return get_user_with_roles(db, user_id)
