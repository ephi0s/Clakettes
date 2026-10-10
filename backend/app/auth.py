"""JWT authentication utilities with refresh token and session support.

Provides access/refresh token creation, decoding, session management,
and a FastAPI dependency that resolves the current authenticated user
from the request ``Authorization`` header.

Token Design:
- Access Token: JWT (HS256), 30 min TTL, contains user_id + type="access"
- Refresh Token: Opaque random string (48 bytes hex), 30 day TTL, stored as SHA-256 hash
- Session: UserSession model tracks device info, IP, user agent, expiry, revocation

Security:
- Tokens validated against DB session (not just JWT signature)
- Refresh token rotation on use (old tokens invalidated)
- last_used_at updated lazily (every 5 min) to reduce DB writes
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session, selectinload
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.models.user_session import UserSession

# OAuth2 scheme for Bearer token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

# Token expiration settings (from config)
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = 30


def _hash_token(token: str) -> str:
    """SHA-256 hash of a token for secure storage.

    Never store raw tokens in database. Hash with SHA-256 before saving.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def _generate_token() -> str:
    """Cryptographically secure random token string (48 bytes = 96 hex chars)."""
    return secrets.token_hex(48)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT with the given payload and optional expiration.

    Args:
        data: Payload dict (must include user_id)
        expires_delta: Optional custom expiration; defaults to ACCESS_TOKEN_EXPIRE_MINUTES

    Returns:
        Signed JWT string with 'exp' and 'type=access' claims
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token() -> str:
    """Generate a cryptographically secure refresh token (opaque, not a JWT).

    Refresh tokens are random strings, not JWTs. They're hashed before storage.
    """
    return _generate_token()


def create_session(
    db: Session,
    user_id: int,
    device_name: str = "",
    ip_address: str = "",
    user_agent: str = "",
) -> tuple[UserSession, str, str]:
    """Create a new user session with access and refresh tokens.

    Args:
        db: Database session
        user_id: User ID to create session for
        device_name: Optional device identifier
        ip_address: Client IP address
        user_agent: Client user agent string

    Returns:
        Tuple of (UserSession, access_token, refresh_token)
    """
    access_token = create_access_token(data={"sub": str(user_id), "user_id": user_id})
    refresh_token = create_refresh_token()

    session = UserSession(
        user_id=user_id,
        token_hash=_hash_token(access_token),
        refresh_token_hash=_hash_token(refresh_token),
        device_name=device_name,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session, access_token, refresh_token


def rotate_refresh_token(db: Session, session: UserSession) -> tuple[str, str]:
    """Rotate tokens within an existing session. Returns (new_access, new_refresh).

    Called on refresh token exchange. Invalidates old tokens by updating hashes.
    """
    new_access = create_access_token(data={"sub": str(session.user_id), "user_id": session.user_id})
    new_refresh = create_refresh_token()
    session.token_hash = _hash_token(new_access)
    session.refresh_token_hash = _hash_token(new_refresh)
    session.last_used_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return new_access, new_refresh


def revoke_session(db: Session, session: UserSession):
    """Mark a session as revoked (logout)."""
    session.revoked_at = datetime.now(timezone.utc)
    session.is_active = False
    db.commit()


def validate_access_token(db: Session, token: str) -> tuple[int, UserSession] | None:
    """Decode a JWT and return ``(user_id, session)`` only if it is a valid access token.

    Validation steps:
    1. Decode JWT and verify signature
    2. Check token type == "access" (reject refresh/typeless tokens)
    3. Look up session by token hash in DB
    4. Verify session is active, not revoked, not expired

    Rejects tokens that are not signed as ``type == "access"`` (refresh or
    typeless tokens) and sessions that are inactive, revoked, or missing.
    Returns ``None`` when validation fails.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int | None = payload.get("user_id")
        if user_id is None or payload.get("type") != "access":
            return None
    except JWTError:
        return None

    # Verify session is active in database
    token_hash = _hash_token(token)
    session = (
        db.query(UserSession)
        .filter(
            UserSession.token_hash == token_hash,
            UserSession.is_active,
            UserSession.revoked_at.is_(None),
        )
        .first()
    )
    if not session:
        return None
    if session.expires_at is not None:
        expires = session.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            return None
    return user_id, session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """FastAPI dependency: decode JWT, verify session, return User or raise 401.

    Flow:
    1. Extract Bearer token from Authorization header
    2. Validate access token via validate_access_token()
    3. Lazily update session.last_used_at (only if >5 min old)
    4. Load User with eager-loaded user_roles + role relationships
    5. Return User or raise 401

    The lazy last_used_at update reduces DB commits on high-traffic endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    result = validate_access_token(db, token)
    if result is None:
        raise credentials_exception
    user_id, session = result

    # Touch last_used_at (lazy, not every request — only if >5 min old)
    now = datetime.now(timezone.utc)
    last_used = session.last_used_at
    if last_used is not None and last_used.tzinfo is None:
        last_used = last_used.replace(tzinfo=timezone.utc)
    if last_used is None or now - last_used >= timedelta(minutes=5):
        session.last_used_at = now
        db.commit()

    # Eager load user_roles with roles for permission checks downstream
    user = (
        db.query(User)
        .options(selectinload(User.user_roles).selectinload(UserRole.role))
        .filter(User.id == user_id)
        .first()
    )
    if user is None:
        raise credentials_exception
    return user
