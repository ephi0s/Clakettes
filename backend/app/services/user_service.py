import bcrypt
import secrets
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from .base_service import BaseService

PRIVACY_POLICY_VERSION = "1.0"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


class UserService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def get_multi_paginated(
        self, db: Session, page: int = 1, size: int = 20, is_active: bool | None = None, role: str | None = None
    ):
        query = db.query(User)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if role:
            query = query.filter(User.role == role)
        return self.paginate(query, page, size)

    def get_public_users(self, db: Session, page: int = 1, size: int = 50) -> list[dict]:
        """Return users with only their publicly visible fields."""
        query = db.query(User).filter(User.is_public)
        users = query.offset((page - 1) * size).limit(size).all()
        return [self.to_public_response(u) for u in users]

    def to_public_response(self, user: User) -> dict:
        """Build a public-safe dict from a User model, respecting per-field privacy."""
        data = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name if user.is_public else None,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "is_active": user.is_active,
            "created_at": user.created_at,
        }
        if user.is_public_email:
            data["email"] = user.email
        if user.is_public_bio:
            data["bio"] = user.bio
        if user.is_public_location:
            data["latitude"] = user.latitude
            data["longitude"] = user.longitude
        return data

    def to_authenticated_public_response(self, user: User) -> dict:
        """Public-safe dict for authenticated non-admin viewers — email never included."""
        data = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name if user.is_public else None,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "is_active": user.is_active,
            "created_at": user.created_at,
        }
        if user.is_public_bio:
            data["bio"] = user.bio
        if user.is_public_location:
            data["latitude"] = user.latitude
            data["longitude"] = user.longitude
        return data

    def create(self, db: Session, obj_in: UserCreate) -> User:
        obj_data = obj_in.model_dump()
        obj_data["password_hash"] = hash_password(obj_data.pop("password"))
        obj_data["privacy_policy_version"] = obj_data.get("privacy_policy_version") or PRIVACY_POLICY_VERSION
        obj_data["privacy_accepted_at"] = obj_data.get("privacy_accepted_at") or datetime.now(timezone.utc)
        db_obj = User(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, username: str, password: str) -> User | None:
        user = self.get_by_username(db, username)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def update(self, db: Session, id: int, obj_in: UserUpdate) -> User | None:
        db_obj = self.get(db, id)
        if not db_obj:
            return None
        update_data = obj_in.model_dump(exclude_unset=True)
        password = update_data.pop("password", None)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        if password:
            db_obj.password_hash = hash_password(password)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def _delete_where(db: Session, model, column, user_id: int) -> int:
        rows = db.query(model).filter(column == user_id).all()
        for row in rows:
            db.delete(row)
        return len(rows)

    @staticmethod
    def _null_where(db: Session, model, *columns, user_id: int) -> int:
        total = 0
        for column in columns:
            total += db.query(model).filter(column == user_id).update({column: None}, synchronize_session=False)
        return total

    def erase_personal_data(self, db: Session, user: User) -> dict:
        """RGPD art. 17 — borra los datos personales del usuario.

        Estrategia: anonimiza la fila de usuario (se conserva por integridad
        referencial de contenidos no personales) y elimina/desvincula el resto.
        """
        from app.models.award import Award
        from app.models.channel import ChannelMember
        from app.models.committee import CommitteeMember
        from app.models.event import Event, EventAttendee, EventReservation
        from app.models.festival_rulebook import FestivalRulebook
        from app.models.form_definition import FormDefinition, FormLink, FormResponse
        from app.models.group import GroupMember
        from app.models.location import Location
        from app.models.notification import Notification
        from app.models.payment import Payment
        from app.models.registration import FestivalRegistration, RegistrationForm, RegistrationFormLink
        from app.models.user_alias import UserAlias
        from app.models.user_festival import user_festival
        from app.models.user_key import UserKey
        from app.models.user_role import UserParticipantTag, UserRole
        from app.models.user_session import UserSession

        if user.role == "admin":
            remaining = db.query(User).filter(User.role == "admin", User.is_active, User.id != user.id).count()
            if remaining == 0:
                raise ValueError("Cannot erase the last active admin account")

        uid = user.id
        summary = {}

        summary["sessions"] = self._delete_where(db, UserSession, UserSession.user_id, uid)
        summary["keys"] = self._delete_where(db, UserKey, UserKey.user_id, uid)
        summary["aliases"] = self._delete_where(db, UserAlias, UserAlias.user_id, uid)
        summary["notifications"] = self._delete_where(db, Notification, Notification.user_id, uid)
        summary["roles"] = self._delete_where(db, UserRole, UserRole.user_id, uid)
        summary["participant_tags"] = self._delete_where(db, UserParticipantTag, UserParticipantTag.user_id, uid)
        reg_ids = [r.id for r in db.query(FestivalRegistration).filter(FestivalRegistration.user_id == uid).all()]
        if reg_ids:
            db.query(Payment).filter(Payment.registration_id.in_(reg_ids)).update(
                {Payment.registration_id: None}, synchronize_session=False
            )
        summary["registrations"] = self._delete_where(db, FestivalRegistration, FestivalRegistration.user_id, uid)
        summary["form_responses"] = self._delete_where(db, FormResponse, FormResponse.user_id, uid)
        summary["attendances"] = self._delete_where(db, EventAttendee, EventAttendee.user_id, uid)
        summary["reservations"] = self._delete_where(db, EventReservation, EventReservation.user_id, uid)
        summary["channel_memberships"] = self._delete_where(db, ChannelMember, ChannelMember.user_id, uid)
        summary["group_memberships"] = self._delete_where(db, GroupMember, GroupMember.user_id, uid)
        summary["committee_memberships"] = self._delete_where(db, CommitteeMember, CommitteeMember.user_id, uid)
        summary["festival_memberships"] = (
            db.execute(user_festival.delete().where(user_festival.c.user_id == uid)).rowcount or 0
        )

        nulled = 0
        nulled += self._null_where(db, UserRole, UserRole.assigned_by, UserRole.approved_by, user_id=uid)
        nulled += self._null_where(db, UserParticipantTag, UserParticipantTag.assigned_by, user_id=uid)
        nulled += self._null_where(
            db,
            FestivalRegistration,
            FestivalRegistration.assigned_by,
            FestivalRegistration.approved_by,
            user_id=uid,
        )
        nulled += self._null_where(db, RegistrationFormLink, RegistrationFormLink.assigned_user_id, user_id=uid)
        nulled += self._null_where(db, RegistrationForm, RegistrationForm.created_by, user_id=uid)
        nulled += self._null_where(db, FormResponse, FormResponse.reviewer_id, user_id=uid)
        nulled += self._null_where(db, FormDefinition, FormDefinition.created_by, user_id=uid)
        nulled += self._null_where(db, FormLink, FormLink.assigned_user_id, user_id=uid)
        nulled += self._null_where(db, Event, Event.created_by, user_id=uid)
        nulled += self._null_where(db, EventAttendee, EventAttendee.invited_by, user_id=uid)
        nulled += self._null_where(db, EventReservation, EventReservation.created_by, user_id=uid)
        nulled += self._null_where(db, Award, Award.user_id, Award.created_by, user_id=uid)
        nulled += self._null_where(db, Location, Location.added_by, user_id=uid)
        nulled += self._null_where(db, FestivalRulebook, FestivalRulebook.created_by, user_id=uid)
        nulled += self._null_where(db, Notification, Notification.related_user_id, user_id=uid)
        summary["unlinked_refs"] = nulled

        avatar_url = user.avatar_url
        user.username = f"deleted-{uid}"
        user.email = f"deleted-{uid}@deleted.local"
        user.password_hash = f"deleted-{secrets.token_hex(16)}"
        user.full_name = None
        user.bio = None
        user.avatar_url = None
        user.latitude = None
        user.longitude = None
        user.is_active = False
        user.is_public = False
        user.is_public_email = False
        user.is_public_bio = False
        user.is_public_location = False
        user.dav_token_hash = None
        user.dav_token_expires_at = None
        user.privacy_policy_version = None
        user.privacy_accepted_at = None
        db.commit()

        if avatar_url and avatar_url.startswith("/uploads/"):
            try:
                from pathlib import Path

                path = Path("uploads") / Path(avatar_url[len("/uploads/") :]).name
                if path.is_file():
                    path.unlink()
                    summary["avatar_file_removed"] = True
            except OSError:
                pass
        return summary

    def export_personal_data(self, db: Session, user: User) -> dict:
        """RGPD art. 20 — devuelve todos los datos personales del usuario en JSON."""
        from app.models.channel import ChannelMember
        from app.models.committee import CommitteeMember
        from app.models.event import Event, EventAttendee, EventReservation
        from app.models.form_definition import FormResponse
        from app.models.group import GroupMember
        from app.models.message import Message
        from app.models.notification import Notification
        from app.models.payment import Payment
        from app.models.registration import FestivalRegistration
        from app.models.shortfilm import ShortFilm
        from app.models.user_alias import UserAlias
        from app.models.user_festival import user_festival
        from app.models.user_key import UserKey
        from app.models.user_role import UserParticipantTag, UserRole
        from app.models.user_session import UserSession

        def row(obj, *fields):
            return {f: getattr(obj, f) for f in fields}

        uid = user.id
        reg_ids = [r.id for r in db.query(FestivalRegistration).filter(FestivalRegistration.user_id == uid).all()]
        data = {
            "profile": row(
                user,
                "id",
                "username",
                "email",
                "full_name",
                "role",
                "bio",
                "avatar_url",
                "is_active",
                "is_public",
                "is_public_email",
                "is_public_bio",
                "is_public_location",
                "latitude",
                "longitude",
                "privacy_policy_version",
                "privacy_accepted_at",
                "created_at",
                "updated_at",
            ),
            "roles": [
                row(r, "id", "role", "festival_id", "assigned_by", "approved_by", "created_at")
                for r in db.query(UserRole).filter(UserRole.user_id == uid).all()
            ],
            "participant_tags": [
                row(t, "id", "tag_id", "festival_id", "assigned_by", "created_at")
                for t in db.query(UserParticipantTag).filter(UserParticipantTag.user_id == uid).all()
            ],
            "aliases": [
                row(a, "id", "alias", "context", "context_id", "notes", "is_public", "created_at")
                for a in db.query(UserAlias).filter(UserAlias.user_id == uid).all()
            ],
            "festivals": [
                {"festival_id": fid, "role": role}
                for fid, role in db.query(user_festival.c.festival_id, user_festival.c.role)
                .filter(user_festival.c.user_id == uid)
                .all()
            ],
            "registrations": [
                row(
                    r,
                    "id",
                    "festival_id",
                    "form_id",
                    "status",
                    "notes",
                    "payment_status",
                    "payment_method",
                    "transaction_id",
                    "paid_at",
                    "created_at",
                )
                for r in db.query(FestivalRegistration).filter(FestivalRegistration.user_id == uid).all()
            ],
            "form_responses": [
                row(r, "id", "form_id", "status", "submitted_at", "review_notes", "created_at")
                for r in db.query(FormResponse).filter(FormResponse.user_id == uid).all()
            ],
            "payments": [
                row(
                    p,
                    "id",
                    "registration_id",
                    "event_id",
                    "amount",
                    "currency",
                    "provider",
                    "status",
                    "provider_ref",
                    "created_at",
                )
                for p in db.query(Payment).filter(Payment.registration_id.in_(reg_ids)).all()
                if reg_ids
            ],
            "messages_sent": [
                row(m, "id", "receiver_id", "group_id", "channel_id", "content", "message_type", "created_at")
                for m in db.query(Message).filter(Message.sender_id == uid).all()
            ],
            "notifications": [
                row(n, "id", "title", "message", "notification_type", "is_read", "created_at")
                for n in db.query(Notification).filter(Notification.user_id == uid).all()
            ],
            "sessions": [
                row(
                    s,
                    "id",
                    "device_name",
                    "ip_address",
                    "user_agent",
                    "last_used_at",
                    "expires_at",
                    "is_active",
                    "created_at",
                )
                for s in db.query(UserSession).filter(UserSession.user_id == uid).all()
            ],
            "shortfilms": [
                row(f, "id", "title", "description", "festival_id", "video_url", "created_at")
                for f in db.query(ShortFilm).filter(ShortFilm.user_id == uid).all()
            ],
            "events_created": [
                row(e, "id", "title", "festival_id", "created_at")
                for e in db.query(Event).filter(Event.created_by == uid).all()
            ],
            "attendances": [
                row(a, "id", "event_id", "created_at")
                for a in db.query(EventAttendee).filter(EventAttendee.user_id == uid).all()
            ],
            "reservations": [
                row(r, "id", "event_id", "created_at")
                for r in db.query(EventReservation).filter(EventReservation.user_id == uid).all()
            ],
            "channel_memberships": [
                row(m, "id", "channel_id", "created_at")
                for m in db.query(ChannelMember).filter(ChannelMember.user_id == uid).all()
            ],
            "group_memberships": [
                row(m, "id", "group_id", "created_at")
                for m in db.query(GroupMember).filter(GroupMember.user_id == uid).all()
            ],
            "committee_memberships": [
                row(m, "id", "committee_id", "created_at")
                for m in db.query(CommitteeMember).filter(CommitteeMember.user_id == uid).all()
            ],
            "public_keys": [
                row(k, "id", "public_key_x25519", "key_identifier", "created_at")
                for k in db.query(UserKey).filter(UserKey.user_id == uid).all()
            ],
        }
        for section in data.values():
            if isinstance(section, list):
                for item in section:
                    for key, value in list(item.items()):
                        if hasattr(value, "isoformat"):
                            item[key] = value.isoformat()
                        elif hasattr(value, "value"):
                            item[key] = value.value
        for key, value in list(data["profile"].items()):
            if hasattr(value, "isoformat"):
                data["profile"][key] = value.isoformat()
        return data
