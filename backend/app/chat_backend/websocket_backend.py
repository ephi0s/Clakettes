"""WebSocket-based chat backend with connection management and broadcast."""

import logging
from typing import Any

from fastapi import WebSocket
from app.chat_backend.base import ChatBackend

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages authenticated WebSocket connections keyed by ``user_id``.

    Thread-safety note: FastAPI WebSocket endpoints run in an async
    context and all methods are called from the same event loop, so no
    locking is needed.
    """

    def __init__(self) -> None:
        # user_id -> list of active WebSocket connections
        self._connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, ws: WebSocket, subprotocol: str | None = None) -> None:
        await ws.accept(subprotocol=subprotocol)
        self._connections.setdefault(user_id, []).append(ws)
        logger.info("WS connected: user_id=%d (total=%d)", user_id, len(self._connections))

    def disconnect(self, user_id: int, ws: WebSocket) -> None:
        conns = self._connections.get(user_id, [])
        if ws in conns:
            conns.remove(ws)
        if not conns:
            self._connections.pop(user_id, None)
        logger.info("WS disconnected: user_id=%d", user_id)

    async def broadcast(self, user_id: int, payload: dict[str, Any]) -> None:
        """Send *payload* to every active connection of *user_id*.

        Dead connections are cleaned up silently.
        """
        conns = self._connections.get(user_id, [])
        dead: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)

    @property
    def active_users(self) -> int:
        return len(self._connections)


class WebSocketChatBackend(ChatBackend):
    """Chat delivery via WebSockets.

    Uses a :class:`ConnectionManager` to track authenticated connections
    and push new messages in real time.

    The WebSocket endpoint that feeds this backend lives in
    ``app.routers.chat`` (``/ws/chat``).
    """

    def __init__(self) -> None:
        self.manager = ConnectionManager()

    async def start(self) -> None:
        logger.info("WebSocketChatBackend started")

    async def stop(self) -> None:
        # Close all active connections gracefully.
        for user_id, conns in list(self.manager._connections.items()):
            for ws in conns:
                try:
                    await ws.close(code=1001, reason="Server shutting down")
                except Exception:
                    pass
        self.manager._connections.clear()
        logger.info("WebSocketChatBackend stopped")

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
            "type": "new_message",
            "message": {
                "id": message_id,
                "content": content,
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "group_id": group_id,
                "channel_id": channel_id,
                "message_type": message_type,
                **extra,
            },
        }

        # Deliver to the direct recipient (P2P).
        if receiver_id is not None:
            await self.manager.broadcast(receiver_id, payload)

        # Group messages are resolved to individual receiver_ids in the
        # router (chat.py) via GroupService.get_members(), so no further
        # logic is needed here.

    async def mark_read(self, message_id: int, user_id: int) -> None:
        """Notify *user_id* that a message was marked as read."""
        payload = {
            "type": "message_read",
            "message_id": message_id,
        }
        await self.manager.broadcast(user_id, payload)
