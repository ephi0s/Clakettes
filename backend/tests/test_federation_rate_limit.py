import os

from fastapi.testclient import TestClient

from app.main import app


def test_federation_rate_limit_blocks(monkeypatch):
    monkeypatch.delenv("TESTING", raising=False)
    monkeypatch.setenv("RATE_LIMITS_DB_PATH", os.path.join(os.getcwd(), "rl_test.db"))
    try:
        os.remove(os.path.join(os.getcwd(), "rl_test.db"))
    except FileNotFoundError:
        pass

    client = TestClient(app)
    for _ in range(60):
        r = client.get("/api/federation/manifest")
        assert r.status_code == 200
    r = client.get("/api/federation/manifest")
    assert r.status_code == 429
