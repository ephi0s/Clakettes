"""CalDAV authentication helpers.

Token hashing mirrors app.auth._hash_token (SHA-256 hex) but tolerates empty
input (returns "") because DAV credentials arrive via URL path segments that
may be absent. Keep both in sync if the hash algorithm ever changes.
"""

import base64
import hashlib
import re
import secrets

from fastapi import HTTPException, Request, Response

from app.dav import constants
from app.models.user import User
from sqlalchemy.orm import Session


PRINCIPAL_ID_RE = re.compile(r"^u\d+$")


def generate_token() -> str:
    """secrets.token_urlsafe(32) — 43 URL-safe chars."""
    return secrets.token_urlsafe(32)


def hash_token(raw: str) -> str:
    """sha256 hexdigest of the raw token, UTF-8 encoded."""
    if not raw:
        return ""
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def user_by_token(db: Session, raw: str) -> User | None:
    """Look up a User by dav_token_hash == hash_token(raw)."""
    if not raw:
        return None
    token_hash = hash_token(raw)
    if not token_hash:
        return None
    return db.query(User).filter(User.dav_token_hash == token_hash).first()


def token_from_request(request: Request) -> str | None:
    """Extract the credential from the request."""
    auth = request.headers.get("authorization")
    if not auth:
        return None
    auth = auth.strip()
    if auth.startswith("Basic "):
        try:
            b64 = auth[6:]
            decoded = base64.b64decode(b64).decode("utf-8")
        except Exception:
            return None
        if ":" in decoded:
            return decoded.split(":", 1)[0]
        return decoded
    if auth.startswith("Bearer "):
        token = auth[7:].strip()
        return token if token else None
    return None


def principal_to_user_id(principal: str) -> int | None:
    """Return the int id when `principal` matches PRINCIPAL_ID_RE."""
    if not principal:
        return None
    if PRINCIPAL_ID_RE.match(principal):
        try:
            return int(principal[1:])
        except ValueError:
            return None
    return None


def resolve_principal_user(db: Session, principal: str, request: Request) -> User:
    """Resolve the {principal} path segment to the authenticated User."""
    if not principal:
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": f'Basic realm="{constants.REALM}"'})

    user_id = principal_to_user_id(principal)
    if user_id is not None:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, headers={"WWW-Authenticate": f'Basic realm="{constants.REALM}"'})
        cred = token_from_request(request)
        resolved = user_by_token(db, cred) if cred else None
        if not resolved or resolved.id != user.id:
            raise HTTPException(status_code=401, headers={"WWW-Authenticate": f'Basic realm="{constants.REALM}"'})
        return user

    resolved = user_by_token(db, principal)
    if not resolved or not resolved.is_active:
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": f'Basic realm="{constants.REALM}"'})
    return resolved


def unauthorized() -> Response:
    """401 JSON response with the WWW-Authenticate challenge header."""
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=401,
        content={"detail": "Unauthorized"},
        headers={"WWW-Authenticate": f'Basic realm="{constants.REALM}"'},
    )
