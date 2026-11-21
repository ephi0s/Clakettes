import base64
import json
from datetime import datetime, timedelta, timezone

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

from app.mtls import cert_fingerprint_sha256


@pytest.fixture
def manifest_keypair(tmp_path, monkeypatch):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key_path = tmp_path / "client.key"
    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "peer.example.org")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("ascii")
    cert_path = tmp_path / "client.crt"
    cert_path.write_text(cert_pem, encoding="utf-8")
    monkeypatch.setenv("MTLS_CLIENT_KEY_PATH", str(key_path))
    monkeypatch.setenv("MTLS_CLIENT_CERT_PATH", str(cert_path))
    return cert, cert_pem


def _manifest_payload(manifest):
    return {k: v for k, v in manifest.items() if k not in ("signature", "certificate_chain")}


def test_set_policy_persists_restriction_flags(client, admin_headers):
    headers, _ = admin_headers
    payload = {
        "node_domain": "peer.example.org",
        "allowed": True,
        "consent_required": False,
        "minimize_data": False,
        "import_only": True,
        "disable_chat": True,
        "disable_search": True,
        "reason": "restriccion",
    }
    response = client.post("/api/federation/nodes", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    flags = ("import_only", "disable_chat", "disable_search")
    assert all(data[flag] for flag in flags)

    listed = client.get("/api/federation/nodes", headers=headers).json()
    stored = next(p for p in listed if p["node_domain"] == payload["node_domain"])
    assert all(stored[flag] for flag in flags)


def test_whoami_returns_jwks_validated_peer(client, monkeypatch):
    from app.routers import federation as federation_router

    service = federation_router.federation_token_service
    token = service.create_token("peer-subject", extra_claims={"issuer_node": "peer.example.org"})

    async def fake_fetch(issuer):
        return service.jwks()

    monkeypatch.setattr(federation_router, "_fetch_peer_jwks", fake_fetch)

    response = client.get("/api/federation/whoami", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {
        "node": "peer.example.org",
        "issuer": service.issuer,
        "subject": "peer-subject",
    }

    invalid = client.get("/api/federation/whoami", headers={"Authorization": "Bearer not-a-jwt"})
    assert invalid.status_code == 401


def test_manifest_is_signed(client, manifest_keypair):
    cert, _ = manifest_keypair
    response = client.get("/api/federation/manifest")
    assert response.status_code == 200
    manifest = response.json()
    assert manifest["expires_at"]
    assert manifest["signature"]
    assert manifest["certificate_chain"]

    canonical = json.dumps(_manifest_payload(manifest), sort_keys=True, separators=(",", ":")).encode("utf-8")
    cert.public_key().verify(base64.b64decode(manifest["signature"]), canonical, padding.PKCS1v15(), hashes.SHA256())


def test_peers_verify_rejects_tampered_manifest(client, manifest_keypair):
    _, cert_pem = manifest_keypair
    registration = client.post(
        "/api/federation/register",
        json={
            "node_domain": "peer.example.org",
            "fingerprint_sha256": cert_fingerprint_sha256(cert_pem),
            "subject_cn": "peer.example.org",
        },
    )
    assert registration.status_code == 200

    manifest = client.get("/api/federation/manifest").json()
    payload = _manifest_payload(manifest)

    valid = client.post(
        "/api/federation/peers/verify",
        json={
            "node_domain": "peer.example.org",
            "certificate_chain": [cert_pem],
            "manifest_signature": manifest["signature"],
            "manifest_payload": payload,
        },
    )
    assert valid.status_code == 200
    assert valid.json()["trusted"] is True

    tampered = dict(payload, version="9.9.9")
    invalid = client.post(
        "/api/federation/peers/verify",
        json={
            "node_domain": "peer.example.org",
            "certificate_chain": [cert_pem],
            "manifest_signature": manifest["signature"],
            "manifest_payload": tampered,
        },
    )
    assert invalid.status_code == 403
