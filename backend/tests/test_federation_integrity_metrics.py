from datetime import datetime, timedelta, timezone

from app.services.federation_metrics_service import FederationMetricsService
from app.services.node_peering_service import NodePeeringService

_PREFIX = "/api/federation"


def test_metrics_matches_resilience_snapshot(client):
    service = FederationMetricsService()
    service.reset()
    service.record("n1.example", 10.0, True)
    service.record("n2.example", 20.0, False, retries=1)
    expected = client.get(f"{_PREFIX}/resilience/metrics").json()
    response = client.get(f"{_PREFIX}/metrics")
    assert response.status_code == 200
    assert response.json() == expected
    service.reset()


def test_integrity_detects_expired_certificate_and_bad_fingerprint(client, db_session):
    NodePeeringService().register_or_update(
        db_session,
        "old.example",
        "not-a-fingerprint",
        not_after=datetime.now(timezone.utc) - timedelta(days=1),
    )
    response = client.get(f"{_PREFIX}/integrity")
    assert response.status_code == 200
    body = response.json()
    assert body["integrity"] is False
    assert "old.example" in body["expired_certificates"]
    assert "old.example" in body["invalid_fingerprints"]
    assert body["manifest_issues"] == []


def test_integrity_ok_when_trusted_nodes_healthy(client, db_session):
    NodePeeringService().register_or_update(
        db_session,
        "good.example",
        "a" * 64,
        not_after=datetime.now(timezone.utc) + timedelta(days=1),
    )
    response = client.get(f"{_PREFIX}/integrity")
    assert response.status_code == 200
    body = response.json()
    assert body["integrity"] is True
    assert body["nodes"] == 1
    assert body["expired_certificates"] == []
    assert body["invalid_fingerprints"] == []
    assert body["manifest_issues"] == []


def test_removed_static_endpoints(client):
    for path in ("fallback", "degrade"):
        response = client.get(f"{_PREFIX}/{path}")
        assert response.status_code == 404
