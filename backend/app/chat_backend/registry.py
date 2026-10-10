from app.chat_backend.base import ChatBackend


class _ChatBackendRegistry:
    """Singleton registry that holds the active :class:`ChatBackend` instance.
    The router layer reads the active backend from here; the lifespan
    hook sets it once at startup.  To swap transports (e.g. WebSockets
    → MQTT) you only change which implementation is registered here.
    """

    def __init__(self) -> None:
        self._backend: ChatBackend | None = None

    def register(self, backend: ChatBackend) -> None:
        """Set the active chat backend (must be called exactly once at startup)."""
        self._backend = backend

    @property
    def backend(self) -> ChatBackend:
        """Return the active backend, or raise if none is registered."""
        if self._backend is None:
            raise RuntimeError("No ChatBackend registered. Call chat_backend_registry.register(...) at startup.")
        return self._backend


chat_backend_registry = _ChatBackendRegistry()
