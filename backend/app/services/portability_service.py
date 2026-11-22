import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from uuid import uuid4

from pydantic import TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app.config import settings
from app.enums import ShortFilmContestType
from app.schemas.common import MediaUrl
from app.models.festival import Festival
from app.models.identity_redirect import IdentityRedirect
from app.models.message import Message
from app.models.migration_audit import MigrationAudit
from app.models.node_policy import NodePolicy
from app.models.shortfilm import ShortFilm
from app.models.user import User
from app.services.node_policy_service import NodePolicyService

_media_url = TypeAdapter(MediaUrl)


def _import_media_url(value):
    if value is None:
        return None
    try:
        return _media_url.validate_python(value)
    except ValidationError:
        return None


def _import_contest_type(value):
    valid = {t.value for t in ShortFilmContestType}
    return value if value in valid else ShortFilmContestType.OFFICIAL_SECTION.value


def _canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class PortabilityService:
    BUNDLE_VERSION = "1"

    def __init__(self):
        self.policy_service = NodePolicyService()

    def _secret(self) -> bytes:
        secret = getattr(settings, "SECRET_KEY", None) or os.environ.get("SECRET_KEY", "")
        return str(secret).encode("utf-8")

    def _sign(self, raw: bytes) -> str:
        return hmac.new(self._secret(), raw, hashlib.sha256).hexdigest()

    def _material(self, bundle: dict) -> bytes | None:
        payload = bundle.get("payload")
        if not isinstance(payload, dict):
            return None
        return _canonical({"origin_domain": bundle.get("origin_domain", ""), "payload": payload})

    def create_bundle(self, db: Session, user: User) -> dict:
        shortfilms = db.query(ShortFilm).filter(ShortFilm.user_id == user.id).order_by(ShortFilm.id).all()
        festival_ids = {sf.festival_id for sf in shortfilms if sf.festival_id}
        festival_ids.update(f.id for f in user.festivals if f.id)
        festivals = (
            db.query(Festival).filter(Festival.id.in_(festival_ids)).order_by(Festival.id).all() if festival_ids else []
        )
        messages = db.query(Message).filter(Message.sender_id == user.id).order_by(Message.id).all()

        payload = {
            "user": {
                "id": user.id,
                "uuid": user.uuid,
                "did": user.did,
                "handle": user.handle,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "bio": user.bio,
                "avatar_url": user.avatar_url,
                "banner_url": user.banner_url,
                "tagline": user.tagline,
                "social_links": user.social_links,
                "is_public": user.is_public,
                "latitude": user.latitude,
                "longitude": user.longitude,
            },
            "shortfilms": [
                {
                    "id": sf.id,
                    "title": sf.title,
                    "description": sf.description,
                    "duration": sf.duration,
                    "video_url": sf.video_url,
                    "thumbnail_url": sf.thumbnail_url,
                    "festival_id": sf.festival_id,
                    "contest_type": sf.contest_type,
                    "tags": sf.tags,
                    "is_public": sf.is_public,
                }
                for sf in shortfilms
            ],
            "festivals": [
                {
                    "id": f.id,
                    "name": f.name,
                    "description": f.description,
                    "location": f.location,
                    "website": f.website,
                    "tagline": f.tagline,
                }
                for f in festivals
            ],
            "messages": [
                {
                    "id": m.id,
                    "content": m.content,
                    "message_type": m.message_type,
                    "receiver_id": m.receiver_id,
                    "group_id": m.group_id,
                    "channel_id": m.channel_id,
                    "media_url": m.media_url,
                }
                for m in messages
            ],
        }

        origin = getattr(settings, "PUBLIC_BASE_URL", None) or "primary"
        raw = _canonical({"origin_domain": origin, "payload": payload})
        return {
            "bundle_version": self.BUNDLE_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "origin_domain": origin,
            "payload": payload,
            "signature": self._sign(raw),
            "checksum": hashlib.sha256(raw).hexdigest(),
        }

    def verify_bundle(self, bundle: dict) -> bool:
        if not isinstance(bundle, dict) or bundle.get("bundle_version") != self.BUNDLE_VERSION:
            return False
        raw = self._material(bundle)
        if raw is None:
            return False
        expected_checksum = hashlib.sha256(raw).hexdigest()
        if not hmac.compare_digest(expected_checksum, str(bundle.get("checksum", ""))):
            return False
        return hmac.compare_digest(self._sign(raw), str(bundle.get("signature", "")))

    def import_bundle(self, db: Session, bundle: dict) -> dict:
        if not self.verify_bundle(bundle):
            raise ValueError("invalid bundle")
        origin = str(bundle.get("origin_domain") or "")
        if not self.policy_service.is_allowed(db, origin):
            raise PermissionError("origin node not allowed")
        policy = db.query(NodePolicy).filter(NodePolicy.node_domain == origin).first()
        minimize = bool(policy.minimize_data) if policy else True
        payload = bundle["payload"]

        user = self._import_user(db, payload.get("user") or {}, origin, minimize)
        shortfilms = self._import_shortfilms(db, payload.get("shortfilms") or [], user)
        festivals = self._import_festivals(db, payload.get("festivals") or [])
        messages = self._import_messages(db, payload.get("messages") or [], user)
        db.commit()
        return {
            "imported": True,
            "origin_domain": origin,
            "minimize_data": minimize,
            "user": 1 if user is not None else 0,
            "shortfilms": shortfilms,
            "festivals": festivals,
            "messages": messages,
        }

    def _import_user(self, db: Session, data: dict, origin: str, minimize: bool) -> User | None:
        if not data:
            return None
        user = None
        for field in ("uuid", "handle", "username", "did"):
            value = data.get(field)
            if value:
                user = db.query(User).filter(getattr(User, field) == value).first()
                if user is not None:
                    break
        if user is None:
            username = data.get("username") or f"imported-{uuid4().hex[:12]}"
            if db.query(User).filter(User.username == username).first():
                username = f"{username}-{uuid4().hex[:6]}"
            email = None if minimize else data.get("email")
            if not email or db.query(User).filter(User.email == email).first():
                email = f"imported-{uuid4().hex[:12]}@placeholder.invalid"
            user = User(username=username, email=email, password_hash="!", is_active=True)
            db.add(user)
            db.flush()
        for field, column in (("uuid", User.uuid), ("handle", User.handle), ("did", User.did)):
            value = data.get(field)
            if value and not db.query(User).filter(column == value, User.id != user.id).first():
                setattr(user, field, value)
        skipped = {"id", "password_hash", "email", "uuid", "handle", "did"}
        if minimize:
            skipped.update({"full_name", "bio", "latitude", "longitude", "social_links"})
        for key, value in data.items():
            if key in skipped or value is None or not hasattr(user, key):
                continue
            setattr(user, key, value)
        return user

    def _import_shortfilms(self, db: Session, items: list[dict], user: User | None) -> int:
        count = 0
        for item in items:
            title = item.get("title")
            if not title:
                continue
            owner_id = user.id if user else -1
            existing = db.query(ShortFilm).filter(ShortFilm.title == title, ShortFilm.user_id == owner_id).first()
            if existing is not None:
                continue
            db.add(
                ShortFilm(
                    title=title,
                    description=item.get("description"),
                    duration=item.get("duration"),
                    video_url=_import_media_url(item.get("video_url")),
                    thumbnail_url=_import_media_url(item.get("thumbnail_url")),
                    contest_type=_import_contest_type(item.get("contest_type")),
                    tags=item.get("tags"),
                    is_public=bool(item.get("is_public", True)),
                    user_id=user.id if user else None,
                )
            )
            count += 1
        return count

    def _import_festivals(self, db: Session, items: list[dict]) -> int:
        count = 0
        for item in items:
            name = item.get("name")
            if not name or db.query(Festival).filter(Festival.name == name).first():
                continue
            db.add(
                Festival(
                    name=name,
                    description=item.get("description"),
                    location=item.get("location"),
                    website=_import_media_url(item.get("website")),
                    tagline=item.get("tagline"),
                )
            )
            count += 1
        return count

    def _import_messages(self, db: Session, items: list[dict], user: User | None) -> int:
        if user is None:
            return 0
        count = 0
        for item in items:
            content = item.get("content")
            if not content:
                continue
            db.add(
                Message(
                    content=content,
                    sender_id=user.id,
                    receiver_id=item.get("receiver_id"),
                    group_id=item.get("group_id"),
                    channel_id=item.get("channel_id"),
                    media_url=item.get("media_url"),
                    message_type=item.get("message_type") or "text",
                )
            )
            count += 1
        return count

    def _festival_integrity(self, festival: Festival, shortfilms: list[ShortFilm]) -> str:
        data = {
            "festival": {
                "id": festival.id,
                "name": festival.name,
                "description": festival.description,
                "location": festival.location,
            },
            "shortfilms": [
                {
                    "id": sf.id,
                    "title": sf.title,
                    "description": sf.description,
                    "duration": sf.duration,
                    "video_url": sf.video_url,
                    "thumbnail_url": sf.thumbnail_url,
                    "tags": sf.tags,
                    "is_public": sf.is_public,
                    "festival_id": sf.festival_id,
                    "contest_type": sf.contest_type,
                }
                for sf in sorted(shortfilms, key=lambda item: item.id or 0)
            ],
        }
        return hashlib.sha256(_canonical(data)).hexdigest()

    def migrate_festival(self, db: Session, festival_id: int, target_domain: str, new_owner_id: int) -> dict:
        festival = db.query(Festival).filter(Festival.id == festival_id).first()
        if festival is None:
            raise LookupError("festival not found")
        owner = db.query(User).filter(User.id == new_owner_id).first()
        if owner is None:
            raise LookupError("owner not found")
        shortfilms = db.query(ShortFilm).filter(ShortFilm.festival_id == festival_id).all()
        checksum_before = self._festival_integrity(festival, shortfilms)

        festival.users = [owner]
        for film in shortfilms:
            film.user_id = new_owner_id
        db.flush()

        remaining = db.query(ShortFilm).filter(ShortFilm.festival_id == festival_id).all()
        checksum_after = self._festival_integrity(festival, remaining)
        if checksum_before != checksum_after:
            db.rollback()
            raise ValueError("integrity check failed")

        db.add(
            MigrationAudit(
                entity_type="festival",
                entity_id=festival.id,
                action="owner_migration",
                source_domain=getattr(settings, "PUBLIC_BASE_URL", None),
                target_domain=target_domain,
                details=json.dumps(
                    {"checksum": checksum_before, "new_owner_id": new_owner_id, "shortfilms": len(remaining)}
                ),
            )
        )
        db.commit()
        return {
            "festival_id": festival.id,
            "new_owner_id": new_owner_id,
            "target_domain": target_domain,
            "shortfilms_preserved": len(remaining),
            "checksum": checksum_before,
            "integrity_ok": True,
        }

    def _new_ref(self, db: Session, user: User, target_domain: str) -> str:
        base = user.handle or user.username
        candidate = f"{base}@{target_domain}"
        if db.query(User).filter(User.handle == candidate, User.id != user.id).first():
            candidate = f"{base}-{user.id}@{target_domain}"
        return candidate

    def migrate_user(self, db: Session, user_ref: str, target_domain: str) -> dict:
        user = (
            db.query(User)
            .filter(
                (User.uuid == user_ref)
                | (User.did == user_ref)
                | (User.handle == user_ref)
                | (User.username == user_ref)
            )
            .first()
        )
        if user is None:
            raise LookupError("user not found")
        new_ref = self._new_ref(db, user, target_domain)
        did = f"did:clakettes:{target_domain}:{user.uuid or user.id}"
        if db.query(User).filter(User.did == did, User.id != user.id).first():
            did = f"{did}-{user.id}"

        user.handle = new_ref
        user.did = did
        db.add(
            IdentityRedirect(
                old_ref=user_ref,
                new_ref=new_ref,
                target_domain=target_domain,
            )
        )
        db.flush()
        db.add(
            MigrationAudit(
                entity_type="user",
                entity_id=user.id,
                action="identity_migration",
                source_domain=getattr(settings, "PUBLIC_BASE_URL", None),
                target_domain=target_domain,
                details=json.dumps({"old_ref": user_ref, "new_ref": new_ref, "did": did}),
            )
        )
        db.commit()
        return {"old_ref": user_ref, "new_ref": new_ref, "target_domain": target_domain, "did": did}

    def get_redirect(self, db: Session, old_ref: str) -> dict | None:
        redirect = db.query(IdentityRedirect).filter(IdentityRedirect.old_ref == old_ref).first()
        if redirect is None:
            return None
        return {
            "old_ref": redirect.old_ref,
            "new_ref": redirect.new_ref,
            "target_domain": redirect.target_domain,
            "created_at": redirect.created_at.isoformat() if redirect.created_at else None,
        }
