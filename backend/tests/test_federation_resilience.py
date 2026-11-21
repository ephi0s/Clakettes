import pytest

from app.main import app
from app.routers import federation_resilience as resilience_router
from app.services.federation_metrics_service import FederationMetricsService
from app.services.node_peering_service import NodePeeringService

_PREFIX = "/api/federation/resilience"

if not any(getattr(route, "path", "").startswith(_PREFIX) for route in app.routes):
    app.include_router(resilience_router.router)


@pytest.fixture(autouse=True)
def _clean_state():
    FederationMetricsService().reset()
    with resilience_router._revocations_lock:
        resilience_router._revocations.clear()
    yield
    FederationMetricsService().reset()
    with resilience_router._revocations_lock:
        resilience_router._revocations.clear()


def _register(db, domain="peer.example", fingerprint="a" * 64):
    return NodePeeringService().register_or_update(db, domain, fingerprint)


def test_health_real(client, db_session):
    response = client.get(f"{_PREFIX}/health")
    assert response.status_code == 200
    body = response.json()
    assert body["database"] == "up"
    assert body["alive"] is True
    assert isinstance(body["node_count"], int)
    assert body["node_count"] == 0

    _register(db_session, "health.example", "b" * 64)
    response = client.get(f"{_PREFIX}/health")
    assert response.status_code == 200
    assert response.json()["node_count"] == 1


def test_heartbeat_updates_last_seen(client, db_session):
    node = _register(db_session, "beat.example", "c" * 64)
    node.last_seen_at = None
    db_session.commit()
    assert node.last_seen_at is None

    response = client.get(f"{_PREFIX}/heartbeat", params={"node": "beat.example"})
    assert response.status_code == 200
    body = response.json()
    assert body["alive"] is True
    assert body["node"] == "beat.example"
    assert body["server_time"]

    db_session.refresh(node)
    assert node.last_seen_at is not None


def test_heartbeat_rejects_unknown_node(client):
    response = client.get(f"{_PREFIX}/heartbeat", params={"node": "unknown.example"})
    assert response.status_code == 404


def test_metrics_after_record(client):
    service = FederationMetricsService()
    service.record("n1.example", 10.0, True)
    service.record("n1.example", 30.0, False)
    service.record("n2.example", 20.0, True, retries=1)

    response = client.get(f"{_PREFIX}/metrics")
    assert response.status_code == 200
    body = response.json()
    assert body["requests"] == 3
    assert body["successes"] == 2
    assert body["failures"] == 1
    assert body["retries"] == 1
    assert body["p50_ms"] == 20.0
    assert body["p95_ms"] == 29.0
    assert body["nodes"]["n1.example"]["requests"] == 2
    assert body["nodes"]["n1.example"]["failures"] == 1
    assert body["nodes"]["n2.example"]["retries"] == 1


def test_revoke_admin_vs_no_admin(client, db_session, admin_headers, auth_headers):
    _register(db_session, "bad.example", "d" * 64)
    admin_h, _ = admin_headers
    user_h, _ = auth_headers

    denied = client.post(
        f"{_PREFIX}/keys/revoke",
        headers=user_h,
        json={"node_domain": "bad.example", "reason": "compromiso"},
    )
    assert denied.status_code == 403

    allowed = client.post(
        f"{_PREFIX}/keys/revoke",
        headers=admin_h,
        json={"node_domain": "bad.example", "reason": "compromiso"},
    )
    assert allowed.status_code == 200
    assert allowed.json()["revoked"] is True

    node = NodePeeringService().get_by_domain(db_session, "bad.example")
    assert node.allowed is False


def test_keys_revoked(client, db_session, admin_headers):
    _register(db_session, "revoked.example", "e" * 64)
    admin_h, _ = admin_headers
    client.post(
        f"{_PREFIX}/keys/revoke",
        headers=admin_h,
        json={"node_domain": "revoked.example", "reason": "fuga de clave"},
    )

    response = client.get(f"{_PREFIX}/keys/revoked")
    assert response.status_code == 200
    items = response.json()["revoked"]
    match = [item for item in items if item["node_domain"] == "revoked.example"]
    assert len(match) == 1
    assert match[0]["reason"] == "fuga de clave"
    assert match[0]["revoked_at"]


def test_incident_plan(client):
    response = client.get(f"{_PREFIX}/incident-plan")
    assert response.status_code == 200
    body = response.json()
    assert body["version"]
    steps = body["steps"]
    assert len(steps) >= 1
    assert [step["step"] for step in steps] == list(range(1, len(steps) + 1))
