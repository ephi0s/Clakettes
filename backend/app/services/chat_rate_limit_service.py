"""In-memory sliding-window chat rate limiting scoped to node and user."""

import math
import time
from collections import deque
from threading import Lock
from urllib.parse import urlparse

from fastapi import Depends, HTTPException, Request

from app.auth import get_current_user
from app.config import settings


class ChatRateLimitService:
    def __init__(self, max_messages: int = 10, window_seconds: int = 60, ttl_seconds: int = 300):
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self.ttl_seconds = ttl_seconds
        self._hits: dict[tuple[str, str], deque[float]] = {}
        self._lock = Lock()

    def _purge(self, now: float) -> None:
        expired = [key for key, hits in self._hits.items() if not hits or now - hits[-1] > self.ttl_seconds]
        for key in expired:
            self._hits.pop(key, None)

    def check(
        self,
        node_domain: str,
        user_id: int | str,
        max_messages: int | None = None,
        window_seconds: int | None = None,
    ) -> tuple[bool, int]:
        limit = self.max_messages if max_messages is None else max_messages
        window = self.window_seconds if window_seconds is None else window_seconds
        key = (str(node_domain or "local"), str(user_id))
        now = time.monotonic()
        with self._lock:
            self._purge(now)
            hits = self._hits.setdefault(key, deque())
            cutoff = now - window
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if len(hits) >= limit:
                retry_after = max(1, math.ceil(hits[0] + window - now))
                return False, retry_after
            hits.append(now)
            return True, 0

    def reset(self, node_domain: str | None = None, user_id: int | str | None = None) -> None:
        with self._lock:
            if node_domain is None and user_id is None:
                self._hits.clear()
                return
            if user_id is None:
                for key in [key for key in self._hits if key[0] == str(node_domain or "local")]:
                    self._hits.pop(key, None)
                return
            self._hits.pop((str(node_domain or "local"), str(user_id)), None)

    def snapshot(self) -> list[dict]:
        with self._lock:
            self._purge(time.monotonic())
            result = []
            for (node_domain, user_id), hits in self._hits.items():
                try:
                    parsed_user_id: int | str = int(user_id)
                except ValueError:
                    parsed_user_id = user_id
                result.append({"node_domain": node_domain, "user_id": parsed_user_id, "count": len(hits)})
            return result


chat_rate_limit = ChatRateLimitService()


def resolve_node_domain(request: Request) -> str:
    peer_domain = getattr(request.state, "peer_domain", None)
    if peer_domain:
        return str(peer_domain)
    configured = getattr(settings, "PUBLIC_BASE_URL", None) or "local"
    configured = str(configured)
    if "://" not in configured:
        configured = f"//{configured}"
    parsed = urlparse(configured)
    return parsed.netloc or parsed.path or "local"


async def enforce_chat_rate_limit(request: Request, current_user=Depends(get_current_user)):
    allowed, retry_after = chat_rate_limit.check(resolve_node_domain(request), current_user.id)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Chat rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )
    return current_user
