import pytest

from app.main import app
from app.models.base import Base
from app.models.festival import Festival
from app.models.shortfilm import ShortFilm
from app.routers.federation_portability import router as portability_router
from app.services.portability_service import IdentityRedirect, MigrationAudit

if not any(getattr(route, "path", "").startswith("/api/federation/portability") for route in app.routes):
    app.include_router(portability_router)


@pytest.fixture(autouse=True)
def _portability_tables(db_session):
    Base.metadata.create_all(
        bind=db_session.get_bind(),
        tables=[IdentityRedirect.__table__, MigrationAudit.__table__],
    )
    yield


def test_export_import_roundtrip(client, auth_headers):
    headers, _ = auth_headers
    exported = client.post("/api/federation/portability/bundles", headers=headers)
    assert exported.status_code == 200
    bundle = exported.json()
    for key in ("bundle_version", "created_at", "origin_domain", "payload", "signature", "checksum"):
        assert key in bundle
    assert set(bundle["payload"]) >= {"user", "shortfilms", "festivals", "messages"}

    imported = client.post("/api/federation/portability/imports", json=bundle, headers=headers)
    assert imported.status_code == 200
    result = imported.json()
    assert result["imported"] is True
    assert result["user"] == 1
    assert result["shortfilms"] == 0


def test_import_tampered_bundle_returns_400(client, auth_headers):
    headers, _ = auth_headers
    bundle = client.post("/api/federation/portability/bundles", headers=headers).json()
    bundle["payload"]["user"]["full_name"] = "Tampered"
    response = client.post("/api/federation/portability/imports", json=bundle, headers=headers)
    assert response.status_code == 400


def test_festival_migration_changes_owner_and_preserves_shortfilms(
    client, auth_headers, admin_headers, create_user, db_session
):
    _, user = auth_headers
    headers, _ = admin_headers
    new_owner, _ = create_user(username="newowner", email="newowner@example.com")
    festival = Festival(name="Festival migrado", users=[user])
    db_session.add(festival)
    db_session.flush()
    films = [ShortFilm(title=f"Corto {index}", user_id=user.id, festival_id=festival.id) for index in range(2)]
    db_session.add_all(films)
    db_session.commit()

    response = client.post(
        f"/api/federation/portability/festivals/{festival.id}/migrate",
        params={"target_domain": "destino.example", "new_owner_id": new_owner.id},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["new_owner_id"] == new_owner.id
    assert data["shortfilms_preserved"] == 2
    assert data["integrity_ok"] is True

    stored = db_session.query(ShortFilm).filter(ShortFilm.festival_id == festival.id).all()
    assert len(stored) == 2
    assert all(film.user_id == new_owner.id for film in stored)
    assert db_session.query(MigrationAudit).filter(MigrationAudit.entity_type == "festival").count() == 1


def test_user_migration_creates_redirect(client, admin_headers, db_session):
    headers, user = admin_headers
    user.handle = "alice"
    db_session.commit()

    response = client.post(
        "/api/federation/portability/users/alice/migrate",
        params={"target_domain": "nuevo.example"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["old_ref"] == "alice"
    assert "nuevo.example" in data["new_ref"]

    redirect = client.get("/api/federation/portability/redirects/alice", headers=headers)
    assert redirect.status_code == 200
    assert redirect.json()["new_ref"] == data["new_ref"]
    assert db_session.query(IdentityRedirect).filter(IdentityRedirect.old_ref == "alice").count() == 1


def test_import_tampered_origin_domain_returns_400(client, auth_headers):
    headers, _ = auth_headers
    bundle = client.post("/api/federation/portability/bundles", headers=headers).json()
    bundle["origin_domain"] = "atacante.example"
    response = client.post("/api/federation/portability/imports", json=bundle, headers=headers)
    assert response.status_code == 400


def test_endpoints_require_authentication(client, db_session):
    bundle = {"bundle_version": "1", "payload": {}, "signature": "x", "checksum": "x"}
    assert client.post("/api/federation/portability/imports", json=bundle).status_code == 401
    festival_url = "/api/federation/portability/festivals/1/migrate?target_domain=x&new_owner_id=1"
    assert client.post(festival_url).status_code == 401
    user_url = "/api/federation/portability/users/alice/migrate?target_domain=x"
    assert client.post(user_url).status_code == 401
    assert client.get("/api/federation/portability/redirects/alice").status_code == 401


def test_migrations_require_admin(client, auth_headers):
    headers, _ = auth_headers
    festival_url = "/api/federation/portability/festivals/1/migrate?target_domain=x&new_owner_id=1"
    assert client.post(festival_url, headers=headers).status_code == 403
    user_url = "/api/federation/portability/users/alice/migrate?target_domain=x"
    assert client.post(user_url, headers=headers).status_code == 403
