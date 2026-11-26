"""Regresiones para las defensas añadidas en la auditoría de seguridad."""

import hashlib
import json

import pytest

from app.config import settings
from app.security import is_safe_peer_domain, validate_secret_key


@pytest.mark.parametrize(
    "domain,expected",
    [
        ("peer.example.org", True),
        ("sub.peer.example.org", True),
        ("127.0.0.1", False),
        ("localhost", False),
        ("peer.example.org:8443", False),
        ("peer.example.org/path", False),
        ("user@peer.example.org", False),
        ("169.254.169.254", False),
        ("", False),
    ],
)
def test_peer_domain_validation(domain, expected):
    assert is_safe_peer_domain(domain) is expected


def test_export_bundle_requires_authorization(client, create_user, db_session):
    user, _ = create_user(username="victim", email="victim@example.com")
    user.handle = "victim"
    db_session.commit()

    assert client.get("/api/federation/export/victim").status_code == 403


def test_export_bundle_allows_self_and_admin(client, create_user, db_session, auth_headers, admin_headers):
    headers, self_user = auth_headers
    self_user.handle = "exporter"
    db_session.commit()

    own = client.get("/api/federation/export/exporter", headers=headers)
    assert own.status_code == 200
    assert own.json()["payload"]["user"]["handle"] == "exporter"

    target, _ = create_user(username="target", email="target@example.com")
    target.handle = "target"
    db_session.commit()
    admin, _ = admin_headers
    assert client.get("/api/federation/export/target", headers=admin).status_code == 200


def test_federation_register_requires_authentication_in_production(client, monkeypatch):
    payload = {"node_domain": "peer.example.org", "fingerprint_sha256": "a" * 64}
    assert client.post("/api/federation/register", json=payload).status_code == 200

    monkeypatch.setattr(settings, "APP_ENV", "production")
    response = client.post("/api/federation/register", json=payload)
    assert response.status_code == 401


def test_federation_register_rejects_unsafe_domain(client):
    payload = {"node_domain": "127.0.0.1", "fingerprint_sha256": "a" * 64}
    assert client.post("/api/federation/register", json=payload).status_code == 400


def test_stream_accepts_bearer_header(client, auth_headers):
    headers, _ = auth_headers
    with client.stream(
        "GET",
        "/api/federation/events/stream",
        params={"limit": 1},
        headers=headers,
    ) as response:
        assert response.status_code == 200


def test_overlong_password_is_rejected_without_hashing(client, admin_headers):
    admin, _ = admin_headers
    response = client.post(
        "/api/users/",
        json={
            "username": "longpass",
            "email": "longpass@example.com",
            "password": "a" * 73,
        },
        headers=admin,
    )
    assert response.status_code == 422


def test_svg_responses_are_sandboxed(client):
    response = client.get("/uploads/does-not-exist.svg")
    assert response.headers["content-security-policy"] == "default-src 'none'; sandbox"


def test_production_validation_rejects_placeholder_secret(monkeypatch):
    monkeypatch.setattr(settings, "APP_ENV", "production")
    monkeypatch.setattr(settings, "SECRET_KEY", "dev-secret-change-in-production")
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        validate_secret_key()


def test_production_validation_requires_db_url_public_origin_and_tls(monkeypatch):
    monkeypatch.setattr(settings, "APP_ENV", "production")
    monkeypatch.setattr(settings, "SECRET_KEY", "x" * 64)
    monkeypatch.setattr(settings, "CORS_ORIGINS", "https://app.example.com")

    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        validate_secret_key()

    monkeypatch.setattr(settings, "DATABASE_URL", "sqlite:///./clakettes.db")
    with pytest.raises(RuntimeError, match="MariaDB"):
        validate_secret_key()

    monkeypatch.setattr(settings, "DATABASE_URL", "mariadb+pymysql://u:p@db:3306/db?ssl_ca=/run/secrets/db-ca.pem")
    with pytest.raises(RuntimeError, match="PUBLIC_BASE_URL"):
        validate_secret_key()

    monkeypatch.setattr(settings, "PUBLIC_BASE_URL", "https://app.example.com")
    validate_secret_key()


def test_imported_bundle_cannot_grant_admin_role(client, auth_headers, db_session):
    from app.models.user import User
    from app.services.portability_service import PortabilityService

    headers, user = auth_headers
    service = PortabilityService()
    bundle = client.post("/api/federation/portability/bundles", headers=headers).json()
    bundle["payload"]["user"]["role"] = "admin"
    bundle["payload"]["user"]["is_active"] = False
    raw = json.dumps(
        {"origin_domain": bundle["origin_domain"], "payload": bundle["payload"]},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    bundle["checksum"] = hashlib.sha256(raw).hexdigest()
    bundle["signature"] = service._sign(raw)

    response = client.post("/api/federation/portability/imports", json=bundle, headers=headers)
    assert response.status_code == 200
    db_session.expire_all()
    stored = db_session.query(User).filter(User.id == user.id).first()
    assert stored.role != "admin"
    assert stored.is_active is True
