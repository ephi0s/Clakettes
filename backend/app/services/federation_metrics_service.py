import threading
from collections import deque

_MAX_SAMPLES = 10000


def _percentile(values, pct):
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(float(ordered[0]), 2)
    rank = (pct / 100.0) * (len(ordered) - 1)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    value = ordered[low] + (ordered[high] - ordered[low]) * (rank - low)
    return round(float(value), 2)


class FederationMetricsService:
    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._lock = threading.Lock()
                    instance._reset_locked()
                    cls._instance = instance
        return cls._instance

    def __init__(self):
        pass

    def _reset_locked(self):
        self._requests = 0
        self._failures = 0
        self._retries = 0
        self._latencies = deque(maxlen=_MAX_SAMPLES)
        self._nodes = {}

    def _node_locked(self, node):
        key = node or "unknown"
        if key not in self._nodes:
            self._nodes[key] = {
                "requests": 0,
                "failures": 0,
                "retries": 0,
                "latencies": deque(maxlen=_MAX_SAMPLES),
            }
        return self._nodes[key]

    def record(self, node, latency_ms, success, retries=0):
        with self._lock:
            self._requests += 1
            self._retries += int(retries or 0)
            if not success:
                self._failures += 1
            try:
                sample = float(latency_ms)
            except (TypeError, ValueError):
                sample = 0.0
            self._latencies.append(sample)
            entry = self._node_locked(node)
            entry["requests"] += 1
            entry["retries"] += int(retries or 0)
            if not success:
                entry["failures"] += 1
            entry["latencies"].append(sample)

    def snapshot(self):
        with self._lock:
            nodes = {}
            for key in sorted(self._nodes):
                entry = self._nodes[key]
                values = list(entry["latencies"])
                nodes[key] = {
                    "requests": entry["requests"],
                    "successes": entry["requests"] - entry["failures"],
                    "failures": entry["failures"],
                    "retries": entry["retries"],
                    "p50_ms": _percentile(values, 50),
                    "p95_ms": _percentile(values, 95),
                }
            values = list(self._latencies)
            return {
                "requests": self._requests,
                "successes": self._requests - self._failures,
                "failures": self._failures,
                "retries": self._retries,
                "p50_ms": _percentile(values, 50),
                "p95_ms": _percentile(values, 95),
                "nodes": nodes,
            }

    def reset(self):
        with self._lock:
            self._reset_locked()
