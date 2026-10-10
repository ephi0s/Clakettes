from abc import ABC, abstractmethod
from typing import Any


class ChatBackend(ABC):
    """Abstract interface for the chat delivery backend.

    Implementations can use WebSockets, MQTT, XMPP/Jabber, or any
    other transport. The rest of the application (routers, services)
    depends on this interface so the transport can be swapped via the
    ``chat_backend_registry`` without changing business logic.
    """

    @abstractmethod
    async def start(self) -> None:
        """Initialise connections, start listeners, etc.

        Called once during application startup (lifespan).
        """

    @abstractmethod
    async def stop(self) -> None:
        """Gracefully shut down all connections and listeners.

        Called once during application shutdown (lifespan).
        """

    @abstractmethod
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
        """Deliver a real-time message to the intended recipient(s).

        Args:
            message_id: The persisted message ID.
            sender_id: The user who sent the message.
            receiver_id: Direct recipient (``None`` for group/channel messages).
            group_id: Legacy group identifier (``None`` for P2P/channel).
            content: The message body.
            message_type: One of ``text``, ``image``, ``location``, ``vcard``, ``ical``.
            channel_id: Channel identifier for room-based messaging.
            **extra: Transport-specific metadata (e.g. ``media_url``, ``latitude``, ``longitude``,
                ``vcard_data``, ``ical_data``, ``created_at``).
        """
