"""RGPD tests: privacy by default, erasure (art. 17), portability (art. 20), retention (art. 5)."""

from datetime import datetime, timedelta, timezone

from app.models.message import Message
from app.models.notification import Notification
from app.models.user import User
from app.models.user_session import UserSession
from app.services.auth_session_service import AuthSessionService
from app.services.user_service import PRIVACY_POLICY_VERSION


def _login(client, username, password):
    response = client.post("/api/users/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()


class TestPrivacyByDefault:
    def test_new_users_are_private_by_default(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.post(
            "/api/users/",
            json={"username": "priv", "email": "priv@example.com", "password": "Strong123"},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["is_public"] is False
        assert data["is_public_email"] is False
        assert data["is_public_bio"] is False
        assert data["is_public_location"] is False

    def test_consent_is_recorded_on_create(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        response = client.post(
            "/api/users/",
            json={"username": "cons", "email": "cons@example.com", "password": "Strong123"},
            headers=headers,
        )
        assert response.status_code == 201
        user = db_session.query(User).filter(User.username == "cons").first()
        assert user.privacy_policy_version == PRIVACY_POLICY_VERSION
        assert user.privacy_accepted_at is not None


class TestRightToErasure:
    def test_delete_me_anonymizes_and_revokes(self, client, create_user, db_session):
        user, password = create_user(username="gone", email="gone@example.com")
        data = _login(client, "gone", password)
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        db_session.add(Notification(user_id=user.id, title="Hi", message="hello", notification_type="test"))
        db_session.add(Message(sender_id=user.id, content="hola", message_type="text"))
        db_session.commit()

        response = client.delete("/api/users/me", headers=headers)
        assert response.status_code == 200
        assert "summary" in response.json()

        db_session.expire_all()
        erased = db_session.query(User).filter(User.id == user.id).first()
        assert erased.username == f"deleted-{user.id}"
        assert erased.email == f"deleted-{user.id}@deleted.local"
        assert erased.full_name is None
        assert erased.is_active is False
        assert db_session.query(UserSession).filter(UserSession.user_id == user.id).count() == 0
        assert db_session.query(Notification).filter(Notification.user_id == user.id).count() == 0
        assert db_session.query(Message).filter(Message.sender_id == user.id).count() == 1

        retry = client.post("/api/users/login", json={"username": "gone", "password": password})
        assert retry.status_code == 401

    def test_delete_me_last_admin_is_blocked(self, client, create_user):
        user, password = create_user(username="solo", email="solo@example.com", role="admin")
        data = _login(client, "solo", password)
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        response = client.delete("/api/users/me", headers=headers)
        assert response.status_code == 400

    def test_admin_can_erase_user_with_content(self, client, admin_headers, create_user, db_session):
        headers, _ = admin_headers
        user, _ = create_user(username="doomed", email="doomed@example.com")
        db_session.add(Message(sender_id=user.id, content="x", message_type="text"))
        db_session.commit()
        response = client.delete(f"/api/users/{user.id}", headers=headers)
        assert response.status_code == 200
        db_session.expire_all()
        erased = db_session.query(User).filter(User.id == user.id).first()
        assert erased.email == f"deleted-{user.id}@deleted.local"


class TestPortability:
    def test_export_my_data(self, client, create_user):
        user, password = create_user(username="expo", email="expo@example.com")
        data = _login(client, "expo", password)
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        response = client.get("/api/users/me/export", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert body["profile"]["email"] == "expo@example.com"
        assert body["profile"]["privacy_policy_version"] == PRIVACY_POLICY_VERSION
        for section in (
            "roles",
            "aliases",
            "registrations",
            "messages_sent",
            "notifications",
            "sessions",
            "shortfilms",
        ):
            assert section in body


class TestRetention:
    def test_purge_expired_sessions(self, db_session, create_user):
        from app.auth import create_session

        user, _ = create_user(username="old", email="old@example.com")
        session, _, _ = create_session(db_session, user.id)
        session.revoked_at = datetime.now(timezone.utc)
        stale, _, _ = create_session(db_session, user.id)
        stale.expires_at = datetime.now(timezone.utc) - timedelta(days=60)
        fresh, _, _ = create_session(db_session, user.id)
        db_session.commit()

        removed = AuthSessionService().purge_expired(db_session)
        assert removed == 2
        remaining = db_session.query(UserSession).filter(UserSession.user_id == user.id).all()
        assert [s.id for s in remaining] == [fresh.id]


class TestDavExpiry:
    def test_token_issued_with_expiry(self, client, create_user):
        user, password = create_user(username="dav1", email="dav1@example.com")
        data = _login(client, "dav1", password)
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        response = client.post("/api/calendar/dav/token", headers=headers)
        assert response.status_code == 200
        assert response.json()["expires_at"] is not None
        status = client.get("/api/calendar/dav/token", headers=headers).json()
        assert status["has_token"] is True
        assert status["expires_at"] is not None

    def test_expired_token_rejected(self, client, create_user, db_session):
        from app.dav.auth import user_by_token

        user, password = create_user(username="dav2", email="dav2@example.com")
        data = _login(client, "dav2", password)
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        raw = client.post("/api/calendar/dav/token", headers=headers).json()["token"]
        assert user_by_token(db_session, raw) is not None
        user.dav_token_expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        db_session.commit()
        assert user_by_token(db_session, raw) is None
        status = client.get("/api/calendar/dav/token", headers=headers).json()
        assert status["has_token"] is False

    def test_regeneration_rotates_expiry(self, client, create_user, db_session):
        user, password = create_user(username="dav3", email="dav3@example.com")
        data = _login(client, "dav3", password)
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        first = client.post("/api/calendar/dav/token", headers=headers).json()["token"]
        user.dav_token_expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        db_session.commit()
        second = client.post("/api/calendar/dav/token", headers=headers).json()["token"]
        assert second != first
        assert client.get("/api/calendar/dav/token", headers=headers).json()["has_token"] is True


class TestTransportSecurity:
    def test_api_carries_strict_csp(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        csp = response.headers["content-security-policy"]
        assert csp.startswith("default-src 'none'")

    def test_docs_keep_relaxed_csp(self, client):
        response = client.get("/docs")
        assert response.status_code == 200
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]

    def test_openapi_is_exportable(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        spec = response.json()
        assert spec["openapi"].startswith("3.")
        ids = [operation.get("operationId") for path in spec["paths"].values() for operation in path.values()]
        assert len(ids) == len(set(ids))
        assert "/api/users/me/export" in spec["paths"]
        assert "/api/admin/audit-log" in spec["paths"]

    def test_hsts_only_in_production(self, client, monkeypatch):
        from app.config import settings

        assert "strict-transport-security" not in client.get("/health").headers
        monkeypatch.setattr(settings, "APP_ENV", "production")
        try:
            assert "max-age=63072000" in client.get("/health").headers["strict-transport-security"]
        finally:
            monkeypatch.setattr(settings, "APP_ENV", "development")

    def test_prod_requires_db_tls(self, monkeypatch):
        from app.config import settings
        from app.main import _validate_secret_key

        monkeypatch.setattr(settings, "APP_ENV", "production")
        monkeypatch.setattr(settings, "SECRET_KEY", "x" * 64)
        monkeypatch.setattr(settings, "CORS_ORIGINS", "https://app.example.com")
        monkeypatch.setattr(settings, "DATABASE_URL", "mariadb+pymysql://u:p@db:3306/clakettes_db")
        try:
            _validate_secret_key()
        except RuntimeError as exc:
            assert "TLS" in str(exc)
        else:
            raise AssertionError("expected RuntimeError without TLS params")
        monkeypatch.setattr(
            settings, "DATABASE_URL", "mariadb+pymysql://u:p@db:3306/clakettes_db?ssl_ca=/run/secrets/db-ca.pem"
        )
        _validate_secret_key()
        monkeypatch.setattr(settings, "DATABASE_URL", "mariadb+pymysql://u:p@db:3306/clakettes_db?ssl=true")
        try:
            _validate_secret_key()
        except RuntimeError as exc:
            assert "ssl_ca" in str(exc)
        else:
            raise AssertionError("expected RuntimeError for bare ?ssl=true")


class TestAuditLog:
    def test_erase_and_export_are_logged(self, client, create_user, db_session):
        from app.models.audit_log import AuditLog

        user, password = create_user(username="aud", email="aud@example.com")
        data = _login(client, "aud", password)
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        client.get("/api/users/me/export", headers=headers)
        client.delete("/api/users/me", headers=headers)
        actions = {a.action for a in db_session.query(AuditLog).filter(AuditLog.actor_user_id == user.id).all()}
        assert "user.export" in actions
        assert "user.erase" in actions

    def test_role_assign_is_logged(self, client, admin_headers, create_user, db_session):
        from app.models.audit_log import AuditLog

        headers, admin = admin_headers
        user, _ = create_user(username="audited", email="audited@example.com")
        role = client.post("/api/roles/", json={"name": "aud_role", "display_name": "Aud"}, headers=headers).json()
        resp = client.post(
            f"/api/users/{user.id}/roles/", json={"user_id": user.id, "role_id": role["id"]}, headers=headers
        )
        assert resp.status_code == 201
        entry = (
            db_session.query(AuditLog)
            .filter(AuditLog.action == "user.role.assign", AuditLog.target_user_id == user.id)
            .first()
        )
        assert entry is not None
        assert entry.actor_user_id == admin.id

    def test_admin_can_list_audit_log(self, client, admin_headers, create_user):
        headers, _ = admin_headers
        user, password = create_user(username="aud2", email="aud2@example.com")
        data = _login(client, "aud2", password)
        client.get("/api/users/me/export", headers={"Authorization": f"Bearer {data['access_token']}"})
        response = client.get("/api/admin/audit-log", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert body["total"] >= 1
        assert any(i["action"] == "user.export" for i in body["items"])

    def test_audit_log_requires_admin(self, client, create_user):
        user, password = create_user(username="aud3", email="aud3@example.com")
        data = _login(client, "aud3", password)
        response = client.get("/api/admin/audit-log", headers={"Authorization": f"Bearer {data['access_token']}"})
        assert response.status_code == 403
