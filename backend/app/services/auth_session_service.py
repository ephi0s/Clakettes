from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.user_session import UserSession
from app.schemas.user_session import UserSessionCreate, UserSessionUpdate
from .base_service import BaseService


class AuthSessionService(BaseService[UserSession, UserSessionCreate, UserSessionUpdate]):
    def __init__(self):
        super().__init__(UserSession)

    def get_by_user(self, db: Session, user_id: int) -> list[UserSession]:
        return (
            db.query(UserSession)
            .filter(
                UserSession.user_id == user_id,
            )
            .order_by(UserSession.last_used_at.desc())
            .all()
        )

    def get_by_refresh_token_hash(self, db: Session, refresh_hash: str) -> UserSession | None:
        return (
            db.query(UserSession)
            .filter(
                UserSession.refresh_token_hash == refresh_hash,
                UserSession.is_active,
                UserSession.revoked_at.is_(None),
            )
            .first()
        )

    def get_user_sessions_paginated(self, db: Session, user_id: int, page: int = 1, size: int = 20) -> dict:
        query = (
            db.query(UserSession)
            .filter(
                UserSession.user_id == user_id,
            )
            .order_by(UserSession.last_used_at.desc())
        )
        return self.paginate(query, page, size)

    def revoke_session(self, db: Session, session_id: int) -> UserSession | None:
        session = self.get(db, session_id)
        if not session:
            return None
        session.revoked_at = datetime.now(timezone.utc)
        session.is_active = False
        db.commit()
        db.refresh(session)
        return session

    def revoke_all_user_sessions(self, db: Session, user_id: int) -> int:
        sessions = (
            db.query(UserSession)
            .filter(
                UserSession.user_id == user_id,
                UserSession.is_active,
            )
            .all()
        )
        now = datetime.now(timezone.utc)
        for s in sessions:
            s.revoked_at = now
            s.is_active = False
        db.commit()
        return len(sessions)

    def purge_expired(self, db: Session, grace_days: int = 30) -> int:
        """RGPD art. 5 — elimina sesiones revocadas o caducadas hace más de `grace_days`.

        Las sesiones simplemente caducadas pero recientes se conservan durante el
        periodo de gracia por auditoría; las revocadas se eliminan siempre.
        """
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(days=grace_days)
        rows = (
            db.query(UserSession)
            .filter(
                (UserSession.revoked_at.is_not(None)) | (UserSession.expires_at < cutoff),
            )
            .all()
        )
        for s in rows:
            db.delete(s)
        db.commit()
        return len(rows)
