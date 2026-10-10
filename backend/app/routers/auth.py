"""Authentication router — handles user login and JWT issuance."""

import os

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserLogin, UserResponse
from app.schemas.user_session import LoginResponse
from app.services.user_service import UserService
from app.auth import create_session

from app.rate_limiter import RateLimiter

router = APIRouter()

_login_limiter = RateLimiter()


def _check_rate_limit(ip: str):
    if os.environ.get("TESTING", "").lower() in ("true", "1"):
        return
    if not _login_limiter.check(f"login:{ip}", 5, 300):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        )


@router.post("/login", response_model=LoginResponse)
async def login(user_login: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Authenticate user by username/password and return JWT with refresh token."""
    ip = request.client.host if request.client else "unknown"
    _check_rate_limit(ip)
    service = UserService()
    user = service.authenticate(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated",
        )
    _login_limiter.reset(f"login:{ip}")

    session, access_token, refresh_token = create_session(
        db,
        user_id=user.id,
        device_name=user_login.device_name or "",
        ip_address=ip,
        user_agent=request.headers.get("user-agent", ""),
    )
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )
