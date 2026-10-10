"""Tests for admin endpoints."""


class TestAdminStats:
    """Tests for GET /api/admin/stats."""

    def test_stats_requires_admin(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/admin/stats", headers=headers)
        assert response.status_code == 403

    def test_stats_requires_auth(self, client):
        response = client.get("/api/admin/stats")
        assert response.status_code == 401

    def test_stats_returns_counts(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.get("/api/admin/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "festivals" in data
        assert "shortfilms" in data
        assert "messages" in data
        assert "active_users" in data
        assert "active_festivals" in data


class TestAdminTables:
    """Tests for GET /api/admin/tables."""

    def test_tables_requires_admin(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/admin/tables", headers=headers)
        assert response.status_code == 403

    def test_tables_returns_table_counts(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.get("/api/admin/tables", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "tables" in data
        tables = data["tables"]
        assert "users" in tables
        assert "festivals" in tables
        assert "shortfilms" in tables
        assert "messages" in tables


class TestAdminReset:
    """Tests for POST /api/admin/reset."""

    def test_reset_requires_confirm(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.post("/api/admin/reset", json={}, headers=headers)
        assert response.status_code == 400

    def test_reset_requires_admin(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post("/api/admin/reset", json={"confirm": "yes"}, headers=headers)
        assert response.status_code == 403

    def test_reset_with_wrong_confirm(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.post("/api/admin/reset", json={"confirm": "no"}, headers=headers)
        assert response.status_code == 400

    def test_reset_with_confirm(self, client, admin_headers, db_session):
        headers, _ = admin_headers
        from app.models.festival import Festival

        db_session.add(Festival(name="ToDelete", is_active=True))
        db_session.commit()
        response = client.post("/api/admin/reset", json={"confirm": "yes", "password": "Test1234"}, headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Database reset complete"
        from app.models.base import Base

        Base.metadata.create_all(bind=db_session.get_bind())
