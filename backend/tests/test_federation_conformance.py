"""Tests de conformidad para nodos de terceros."""

import json

from app.services.federation_conformance_service import FederationConformanceService

MANIFEST_PATH = "/api/federation/manifest"
JWKS_PATH = "/api/federation/.well-known/jwks.json"


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload
        self.text = json.dumps(payload)

    def json(self) -> dict:
        return self._payload


class _OverridingClient:
    def __init__(self, delegate, overrides: dict):
        self._delegate = delegate
        self._overrides = overrides

    def get(self, path: str, **kwargs):
        if path in self._overrides:
            return self._overrides[path]
        return self._delegate.get(path, **kwargs)

    def post(self, path: str, **kwargs):
        if path in self._overrides:
            return self._overrides[path]
        return self._delegate.post(path, **kwargs)


def _run(client) -> dict:
    return FederationConformanceService(client).run()


def _check(report: dict, check_id: str) -> dict:
    return next(item for item in report["checks"] if item["id"] == check_id)


def test_conforming_node_scores_high_without_severe_failures(client):
    report = _run(client)
    assert report["score"] >= 90
    assert report["severe_failures"] == 0
    assert report["failed"] <= 1
    assert report["schema_version"] == "1"


def test_manifest_without_signature_is_a_severe_failure(client):
    manifest = client.get(MANIFEST_PATH).json()
    manifest.pop("signature", None)
    node = _OverridingClient(client, {MANIFEST_PATH: _FakeResponse(200, manifest)})
    report = _run(node)
    check = _check(report, "manifest")
    assert check["passed"] is False
    assert check["severity"] == "critical"
    assert check["detail"] == "manifest_signature_missing"
    assert report["severe_failures"] >= 1


def test_invalid_jwks_is_reported_as_failure(client):
    jwks = {"keys": [{"kty": "oct", "k": "not-an-rsa-key"}]}
    node = _OverridingClient(client, {JWKS_PATH: _FakeResponse(200, jwks)})
    report = _run(node)
    check = _check(report, "jwks")
    assert check["passed"] is False
    assert check["detail"] == "jwks_invalid"


def test_missing_endpoints_are_failed_without_raising(client):
    missing = _FakeResponse(404, {"detail": "Not Found"})
    node = _OverridingClient(
        client,
        {
            MANIFEST_PATH: missing,
            "/api/federation/chat/bridge/config": missing,
        },
    )
    report = _run(node)
    assert report["failed"] >= 2
    assert _check(report, "chat_bridge")["detail"] == "chat_bridge_missing"
    assert _check(report, "manifest")["detail"] == "manifest_unavailable"


def test_report_is_json_serializable(client):
    json.dumps(_run(client))
