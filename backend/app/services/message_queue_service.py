import base64
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def canonical_json(fields: dict[str, Any]) -> bytes:
    return json.dumps(fields, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


class ChatOutbox(Base):
    __tablename__ = "chat_outbox"
    __table_args__ = (UniqueConstraint("message_id", name="uq_chat_outbox_message_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String(36), nullable=False, index=True)
    node_origin = Column(String(255), nullable=False, index=True)
    subject = Column(String(255), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    signature = Column(Text, nullable=True)
    status = Column(String(16), nullable=False, default="pending", index=True)
    attempts = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_utcnow, index=True)


class MessageTransport(Protocol):
    async def publish(self, envelope: dict[str, Any]) -> None: ...


def _deliver(backend: Any, envelope: dict[str, Any]) -> Any:
    payload = envelope.get("payload") or {}
    return backend.send_message(
        message_id=payload.get("db_message_id", 0),
        sender_id=payload.get("sender_id", 0),
        receiver_id=payload.get("receiver_id"),
        group_id=payload.get("group_id"),
        content=payload.get("content", ""),
        message_type=payload.get("message_type", "text"),
        channel_id=payload.get("channel_id"),
    )


class RegistryTransport:
    async def publish(self, envelope: dict[str, Any]) -> None:
        from app.chat_backend.registry import chat_backend_registry

        try:
            backend = chat_backend_registry.backend
        except RuntimeError:
            return
        if getattr(backend, "_is_durable_queue_backend", False):
            return
        await _deliver(backend, envelope)


class ChatBackendTransport:
    def __init__(self, backend: Any) -> None:
        self._backend = backend

    async def publish(self, envelope: dict[str, Any]) -> None:
        await _deliver(self._backend, envelope)


class NullTransport:
    async def publish(self, envelope: dict[str, Any]) -> None:
        return None


class MessageQueueService:
    def __init__(
        self,
        transport: MessageTransport | None = None,
        max_attempts: int = 3,
        backoff_base_seconds: float = 1.0,
    ) -> None:
        self._transport = transport or RegistryTransport()
        self._max_attempts = max_attempts
        self._backoff_base_seconds = backoff_base_seconds

    def get_by_message_id(self, db: Session, message_id: str) -> ChatOutbox | None:
        return db.query(ChatOutbox).filter(ChatOutbox.message_id == str(message_id)).first()

    def enqueue(
        self,
        db: Session,
        *,
        message_id: str | uuid.UUID,
        node_origin: str,
        subject: str,
        payload: dict[str, Any],
        signature: str | None = None,
    ) -> ChatOutbox:
        mid = str(message_id)
        existing = self.get_by_message_id(db, mid)
        if existing is not None:
            return existing
        row = ChatOutbox(
            message_id=mid,
            node_origin=node_origin,
            subject=subject,
            payload=payload,
            signature=signature,
            status="pending",
            attempts=0,
        )
        db.add(row)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            existing = self.get_by_message_id(db, mid)
            if existing is not None:
                return existing
            raise
        db.refresh(row)
        return row

    def _is_due(self, row: ChatOutbox, now: datetime) -> bool:
        if (row.attempts or 0) <= 0:
            return True
        delay = self._backoff_base_seconds * (2 ** (min(row.attempts, 10) - 1))
        return (row.created_at or now) <= now - timedelta(seconds=delay)

    def pending(self, db: Session, *, limit: int | None = None) -> list[ChatOutbox]:
        rows = (
            db.query(ChatOutbox)
            .filter(ChatOutbox.status == "pending")
            .order_by(ChatOutbox.created_at.asc(), ChatOutbox.id.asc())
            .all()
        )
        now = _utcnow()
        due = [row for row in rows if self._is_due(row, now)]
        return due[:limit] if limit is not None else due

    def mark_sent(self, db: Session, outbox_id: int) -> None:
        row = db.query(ChatOutbox).filter(ChatOutbox.id == outbox_id).first()
        if row is None:
            return
        row.status = "sent"
        row.last_error = None
        db.commit()

    def mark_failed(self, db: Session, outbox_id: int, error: str) -> None:
        row = db.query(ChatOutbox).filter(ChatOutbox.id == outbox_id).first()
        if row is None:
            return
        row.attempts = (row.attempts or 0) + 1
        row.last_error = (error or "")[:1000]
        if row.attempts >= self._max_attempts:
            row.status = "failed"
        db.commit()

    async def flush_pending(self, db: Session, *, limit: int | None = None) -> list[ChatOutbox]:
        processed: list[ChatOutbox] = []
        for row in self.pending(db, limit=limit):
            envelope = {
                "message_id": row.message_id,
                "node_origin": row.node_origin,
                "subject": row.subject,
                "payload": row.payload,
                "signature": row.signature,
            }
            try:
                await self._transport.publish(envelope)
                self.mark_sent(db, row.id)
            except Exception as exc:
                self.mark_failed(db, row.id, f"{type(exc).__name__}: {exc}")
            processed.append(row)
        return processed

    def sign_envelope(self, envelope: dict[str, Any], private_pem: str) -> str:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        key = serialization.load_pem_private_key(private_pem.encode("ascii"), password=None)
        fields = {k: v for k, v in envelope.items() if k != "signature"}
        signature = key.sign(canonical_json(fields), padding.PKCS1v15(), hashes.SHA256())
        return base64.b64encode(signature).decode("ascii")
