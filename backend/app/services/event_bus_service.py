import asyncio
import threading
import time
import uuid
from collections import deque
from datetime import datetime, timezone

CACHE_INVALIDATION_TOPIC = "cache:invalidation"
NEW_FESTIVAL_TOPIC = "festival:new"
BACKOFF_SCHEDULE = (0.3, 1.5, 5.0)


def node_topic(domain):
    return f"node:{domain}"


def entity_topic(entity, entity_id=None):
    return f"entity:{entity}" + (f":{entity_id}" if entity_id else "")


class EventBusService:
    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    obj = super().__new__(cls)
                    obj._state_lock = threading.RLock()
                    obj._retry_lock = threading.RLock()
                    obj._topics = {}
                    obj._retries = {}
                    obj._replay_limit = 200
                    obj._max_attempts = 3
                    cls._instance = obj
        return cls._instance

    def _topic_state(self, topic):
        with self._state_lock:
            state = self._topics.get(topic)
            if state is None:
                state = {"sequence": 0, "replay": deque(maxlen=self._replay_limit), "subscribers": {}}
                self._topics[topic] = state
            return state

    def subscribe(self, topic):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        sub_id = uuid.uuid4().hex
        state = self._topic_state(topic)
        with self._state_lock:
            state["subscribers"][sub_id] = {
                "id": sub_id,
                "queue": asyncio.Queue(),
                "loop": loop,
                "thread_id": threading.get_ident(),
            }
        return sub_id, state["subscribers"][sub_id]["queue"]

    def unsubscribe(self, topic, sub_id):
        state = self._topic_state(topic)
        with self._state_lock:
            state["subscribers"].pop(sub_id, None)

    @staticmethod
    def _deliver_envelope(sub, envelope):
        loop = sub["loop"]
        try:
            if loop is not None and loop.is_running() and sub["thread_id"] != threading.get_ident():
                loop.call_soon_threadsafe(sub["queue"].put_nowait, envelope)
            else:
                sub["queue"].put_nowait(envelope)
        except Exception:
            pass

    def publish(self, topic, event):
        state = self._topic_state(topic)
        with self._state_lock:
            state["sequence"] += 1
            seq = state["sequence"]
            envelope = {
                "seq": seq,
                "topic": topic,
                "type": event.get("type", "message"),
                "node": event.get("node"),
                "data": event.get("data", {}),
                "timestamp": event.get("timestamp") or datetime.now(timezone.utc).isoformat(),
            }
            state["replay"].append(envelope)
            subscribers = list(state["subscribers"].values())
        for sub in subscribers:
            self._deliver_envelope(sub, envelope)
        return envelope

    def replay(self, topic, since=0):
        state = self._topic_state(topic)
        with self._state_lock:
            return [event for event in state["replay"] if event["seq"] > since]

    def latest_sequence(self, topic):
        with self._state_lock:
            state = self._topics.get(topic)
            return state["sequence"] if state else 0

    @staticmethod
    def _backoff(attempt):
        return BACKOFF_SCHEDULE[min(attempt, len(BACKOFF_SCHEDULE) - 1)]

    def enqueue_retry(self, node_domain, event, error=None):
        retry_id = uuid.uuid4().hex
        item = {
            "id": retry_id,
            "node_domain": node_domain,
            "event": event,
            "attempt": 0,
            "max_attempts": self._max_attempts,
            "next_attempt_at": time.time() + self._backoff(0),
            "last_error": error,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        with self._retry_lock:
            self._retries[retry_id] = item
        return dict(item)

    def due_retries(self, now=None):
        now = time.time() if now is None else now
        with self._retry_lock:
            return [dict(item) for item in self._retries.values() if item["next_attempt_at"] <= now]

    def acknowledge_retry(self, retry_id):
        with self._retry_lock:
            return self._retries.pop(retry_id, None) is not None

    def fail_retry(self, retry_id, error=None):
        with self._retry_lock:
            item = self._retries.get(retry_id)
            if item is None:
                return None
            item["attempt"] += 1
            item["last_error"] = error
            if item["attempt"] >= item["max_attempts"]:
                self._retries.pop(retry_id, None)
                return None
            item["next_attempt_at"] = time.time() + self._backoff(item["attempt"])
            return dict(item)

    def list_retries(self):
        with self._retry_lock:
            return [dict(item) for item in self._retries.values()]

    def reset(self):
        with self._state_lock:
            self._topics.clear()
        with self._retry_lock:
            self._retries.clear()


event_bus = EventBusService()
