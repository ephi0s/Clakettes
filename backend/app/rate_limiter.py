import sqlite3
import time
import threading
from pathlib import Path

_CLEANUP_INTERVAL = 300


class RateLimiter:
    """SQLite-backed rate limiter that works across multiple workers."""

    _local = threading.local()

    def __init__(self, db_path: str | None = None):
        import os

        if db_path is None:
            env_path = os.environ.get("RATE_LIMITS_DB_PATH")
            if env_path:
                db_path = env_path
            else:
                db_path = str(Path(__file__).parent.parent / "rate_limits.db")
        self._db_path = db_path
        self._last_cleanup = 0.0
        self._init_db()

    @property
    def _conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(self._db_path)
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
        return self._local.conn

    def _init_db(self):
        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    key TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rate_limits_key ON rate_limits(key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rate_limits_ts ON rate_limits(timestamp)")
            conn.commit()
        finally:
            conn.close()

    def _periodic_cleanup(self):
        now = time.time()
        if now - self._last_cleanup < _CLEANUP_INTERVAL:
            return
        self._last_cleanup = now
        cutoff = now - 3600
        conn = self._conn
        conn.execute("DELETE FROM rate_limits WHERE timestamp < ?", (cutoff,))
        conn.commit()

    def check(self, key: str, max_attempts: int, window: int) -> bool:
        """Returns True if allowed, False if rate limited."""
        now = time.time()
        cutoff = now - window
        conn = self._conn
        conn.execute("DELETE FROM rate_limits WHERE key = ? AND timestamp < ?", (key, cutoff))
        count = conn.execute(
            "SELECT COUNT(*) FROM rate_limits WHERE key = ? AND timestamp >= ?", (key, cutoff)
        ).fetchone()[0]
        if count >= max_attempts:
            conn.commit()
            return False
        conn.execute("INSERT INTO rate_limits (key, timestamp) VALUES (?, ?)", (key, now))
        conn.commit()
        self._periodic_cleanup()
        return True

    def reset(self, key: str):
        conn = self._conn
        conn.execute("DELETE FROM rate_limits WHERE key = ?", (key,))
        conn.commit()
