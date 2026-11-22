import pytest

from app.auth import create_session
from app.models.user import User
from app.routers import federation as federation_router
from app.routers import federation_events as federation_events_router


def test_erase_unknown_ref_returns_404(client, auth_headers):
    headers, _ = auth_headers
    response = client.delete("/api/federation/users/no-such-user", headers=headers)
    assert response.status_code == 404


def test_erase_requires_authorization(client, create_user, db_session):
    user, _ = create_user(username="victim", email="victim@example.com")
    user.handle = "victim"
    db_session.commit()

    assert client.delete("/api/federation/users/victim").status_code == 403

    other, _ = create_user(username="other", email="other@example.com")
    session, token, _ = create_session(db_session, other.id)
    response = client.delete("/api/federation/users/victim", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_self_erase_is_real_and_emits_event(client, auth_headers, db_session):
    headers, user = auth_headers
    user.handle = "selfie"
    user.did = "did:clakettes:primary:selfie"
    db_session.commit()

    response = client.delete("/api/federation/users/selfie", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["erased"] is True
    assert data["ref"] == "selfie"
    assert data["user_id"] == user.id
    assert "summary" in data
    assert data["propagated"] == []
    assert data["failed"] == []

    erased = db_session.query(User).filter(User.id == user.id).first()
    assert erased.username == f"deleted-{user.id}"
    assert erased.email == f"deleted-{user.id}@deleted.local"
    assert erased.is_active is False


def test_admin_can_erase_other_user(client, admin_headers, create_user, db_session):
    headers, _ = admin_headers
    target, _ = create_user(username="target", email="target@example.com")
    target.handle = "target@peer.example.org"
    db_session.commit()

    response = client.delete("/api/federation/users/target@peer.example.org", headers=headers)
    assert response.status_code == 200
    assert response.json()["user_id"] == target.id
    assert db_session.query(User).filter(User.id == target.id).first().is_active is False


def test_last_admin_erase_returns_400(client, admin_headers):
    headers, admin = admin_headers
    response = client.delete(f"/api/federation/users/{admin.username}", headers=headers)
    assert response.status_code == 400


def test_verified_peer_can_erase_its_own_scoped_ref(client, create_user, db_session, monkeypatch):
    from app.services.node_peering_service import NodePeeringService

    user, _ = create_user(username="remote", email="remote@example.com")
    user.handle = "remote@peer.example.org"
    db_session.commit()

    service = federation_router.federation_token_service
    token = service.create_token("peer-subject", extra_claims={"issuer_node": "peer.example.org"})

    async def fake_fetch(issuer):
        return service.jwks()

    async def fake_send(domain, envelope):
        assert envelope["type"] == "user.erase"
        return True

    monkeypatch.setattr(federation_router, "_fetch_peer_jwks", fake_fetch)
    monkeypatch.setattr(federation_events_router, "_send_to_peer", fake_send)
    NodePeeringService().register_or_update(db_session, "peer.example.org", "a" * 64, allowed=True)

    peer_headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/api/federation/users/remote@peer.example.org", headers=peer_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["erased"] is True
    assert data["propagated"] == ["peer.example.org"]
    assert data["failed"] == []
    assert db_session.query(User).filter(User.id == user.id).first().is_active is False

    other, _ = create_user(username="local", email="local@example.com")
    other.handle = "local@primary.example.org"
    db_session.commit()
    forbidden = client.delete("/api/federation/users/local@primary.example.org", headers=peer_headers)
    assert forbidden.status_code == 403


@pytest.mark.parametrize("token_value", ["not-a-jwt", ""])
def test_invalid_peer_token_cannot_erase(client, create_user, db_session, token_value):
    user, _ = create_user(username="victim2", email="victim2@example.com")
    user.handle = "victim2@peer.example.org"
    db_session.commit()

    headers = {"Authorization": f"Bearer {token_value}"} if token_value else {}
    response = client.delete("/api/federation/users/victim2@peer.example.org", headers=headers)
    assert response.status_code == 403
