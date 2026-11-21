import uuid
from typing import Any

from app import database as app_database
from app.chat_backend.base import ChatBackend
from app.services.message_queue_service import MessageQueueService


class DurableQueueBackend(ChatBackend):
    _is_durable_queue_backend = True

    def __init__(
        self,
        queue: MessageQueueService,
        delegate: ChatBackend | None = None,
        session_factory: Any = None,
        node_origin: str = "local",
    ) -> None:
        self._queue = queue
        self._delegate = delegate
        self._session_factory = session_factory or (lambda: app_database.SessionLocal())
        self._node_origin = node_origin
        self._started = False

    async def start(self) -> None:
        if self._delegate is not None:
            await self._delegate.start()
        db = self._session_factory()
        try:
            await self._queue.flush_pending(db)
        finally:
            db.close()
        self._started = True

    async def stop(self) -> None:
        db = self._session_factory()
        try:
            await self._queue.flush_pending(db)
        finally:
            db.close()
        if self._delegate is not None:
            await self._delegate.stop()
        self._started = False

    async def send_message(
        self,
        *,
        message_id: int,
        sender_id: int,
        receiver_id: int | None,
        group_id: int | None,
        content: str,
        message_type: str = "text",
        channel_id: int | None = None,
        **extra: Any,
    ) -> None:
        payload: dict[str, Any] = {
            "db_message_id": message_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "group_id": group_id,
            "channel_id": channel_id,
            "content": content,
            "message_type": message_type,
            **{k: v for k, v in extra.items() if k != "signature"},
        }
        if channel_id is not None:
            subject = f"clakettes.chat.{channel_id}"
        elif receiver_id is not None:
            subject = f"clakettes.chat.direct.{receiver_id}"
        else:
            subject = "clakettes.chat.broadcast"

        db = self._session_factory()
        try:
            outbox = self._queue.enqueue(
                db,
                message_id=uuid.uuid4(),
                node_origin=self._node_origin,
                subject=subject,
                payload=payload,
            )
            envelope = {
                "message_id": outbox.message_id,
                "node_origin": outbox.node_origin,
                "subject": outbox.subject,
                "payload": outbox.payload,
                "signature": outbox.signature,
            }
            try:
                await self._queue._transport.publish(envelope)
                self._queue.mark_sent(db, outbox.id)
            except Exception as exc:
                self._queue.mark_failed(db, outbox.id, f"{type(exc).__name__}: {exc}")
        finally:
            db.close()

    @property
    def manager(self) -> Any | None:
        return getattr(self._delegate, "manager", None)

    async def mark_read(self, message_id: int, user_id: int) -> None:
        if self._delegate is not None and hasattr(self._delegate, "mark_read"):
            await self._delegate.mark_read(message_id, user_id)
