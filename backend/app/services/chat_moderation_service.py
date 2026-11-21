"""Chat moderation: reports, message moderation, channel mutes and node chat policy."""

from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.base import BaseModel
from app.models.channel import ChannelMember
from app.models.message import Message
from app.models.node_policy import NodePolicy
from app.routers.permissions import is_admin


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class MessageReport(BaseModel):
    __tablename__ = "message_reports"

    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, index=True)
    reason = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default="pending", index=True)


class ChatMute(BaseModel):
    __tablename__ = "chat_mutes"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=True, index=True)
    node_domain = Column(String(255), nullable=True, index=True)
    until = Column(DateTime, nullable=False)
    reason = Column(String(500), nullable=True)


class ChatModerationService:
    def __init__(self, blocked_words: list[str] | set[str] | None = None):
        self.blocked_words: set[str] = set()
        if blocked_words:
            self.set_blocked_words(blocked_words)

    def set_blocked_words(self, words) -> None:
        self.blocked_words = {str(word).strip().lower() for word in words if str(word).strip()}

    def add_blocked_word(self, word: str) -> None:
        cleaned = str(word).strip().lower()
        if cleaned:
            self.blocked_words.add(cleaned)

    def remove_blocked_word(self, word: str) -> None:
        self.blocked_words.discard(str(word).strip().lower())

    def contains_blocked_word(self, content: str | None) -> bool:
        text = (content or "").lower()
        return any(word in text for word in self.blocked_words)

    def _can_moderate(self, db: Session, user, channel_id: int | None = None) -> bool:
        if is_admin(user, db):
            return True
        if channel_id is None:
            return False
        membership = (
            db.query(ChannelMember)
            .filter(
                ChannelMember.channel_id == channel_id,
                ChannelMember.user_id == user.id,
                ChannelMember.role.in_(("admin", "moderator")),
                ChannelMember.is_active.is_(True),
            )
            .first()
        )
        return membership is not None

    def report_message(self, db: Session, reporter_id: int, message_id: int, reason: str) -> MessageReport:
        message = db.query(Message).filter(Message.id == message_id).first()
        if message is None:
            raise HTTPException(status_code=404, detail="Message not found")
        report = MessageReport(reporter_id=reporter_id, message_id=message_id, reason=reason, status="pending")
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    def list_reports(
        self, db: Session, status: str | None = None, page: int = 1, size: int = 50
    ) -> list[MessageReport]:
        query = db.query(MessageReport)
        if status:
            query = query.filter(MessageReport.status == status)
        return query.order_by(MessageReport.created_at.desc()).offset((page - 1) * size).limit(size).all()

    def moderate_message(self, db: Session, message_id: int, action: str, user) -> dict:
        message = db.query(Message).filter(Message.id == message_id).first()
        if message is None:
            raise HTTPException(status_code=404, detail="Message not found")
        if not self._can_moderate(db, user, message.channel_id):
            raise HTTPException(status_code=403, detail="Only admins and channel moderators can moderate messages")
        if action == "delete":
            db.delete(message)
            db.commit()
            return {"message_id": message_id, "action": "delete", "status": "deleted"}
        if action == "hide":
            message.content = "[hidden by moderator]"
            message.media_url = None
            message.vcard_data = None
            message.ical_data = None
            db.commit()
            db.refresh(message)
            return {"message_id": message_id, "action": "hide", "status": "hidden"}
        raise HTTPException(status_code=400, detail="Invalid moderation action")

    def mute_user(
        self,
        db: Session,
        user_id: int,
        actor,
        channel_id: int | None = None,
        node_domain: str | None = None,
        duration_seconds: int = 3600,
        reason: str | None = None,
    ) -> ChatMute:
        if not self._can_moderate(db, actor, channel_id):
            raise HTTPException(status_code=403, detail="Only admins and channel moderators can mute users")
        mute = ChatMute(
            user_id=user_id,
            channel_id=channel_id,
            node_domain=node_domain,
            until=_utcnow() + timedelta(seconds=duration_seconds),
            reason=reason,
        )
        db.add(mute)
        db.commit()
        db.refresh(mute)
        return mute

    def list_mutes(self, db: Session, include_expired: bool = False) -> list[ChatMute]:
        query = db.query(ChatMute)
        if not include_expired:
            query = query.filter(ChatMute.until > _utcnow())
        return query.order_by(ChatMute.until.desc()).all()

    def is_muted(
        self,
        db: Session,
        user_id: int,
        channel_id: int | None = None,
        node_domain: str | None = None,
    ) -> bool:
        query = db.query(ChatMute).filter(ChatMute.user_id == user_id, ChatMute.until > _utcnow())
        if channel_id is not None:
            query = query.filter(or_(ChatMute.channel_id.is_(None), ChatMute.channel_id == channel_id))
        if node_domain is not None:
            query = query.filter(or_(ChatMute.node_domain.is_(None), ChatMute.node_domain == node_domain))
        return query.first() is not None

    def is_chat_disabled(self, db: Session, node_domain: str) -> bool:
        policy = db.query(NodePolicy).filter(NodePolicy.node_domain == node_domain).first()
        return bool(policy and policy.disable_chat)

    def check_send_allowed(
        self,
        db: Session,
        user_id: int,
        node_domain: str | None = None,
        channel_id: int | None = None,
        content: str | None = None,
    ) -> bool:
        if node_domain and self.is_chat_disabled(db, node_domain):
            raise HTTPException(status_code=403, detail="Chat is disabled for this node")
        if self.is_muted(db, user_id, channel_id=channel_id, node_domain=node_domain):
            raise HTTPException(status_code=403, detail="User is muted")
        if content is not None and self.contains_blocked_word(content):
            raise HTTPException(status_code=400, detail="Message contains blocked words")
        return True
