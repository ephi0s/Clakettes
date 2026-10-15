"""Tests for profile badges (insignias) endpoints."""


def _login(client, create_user, username, email, role="user"):
    user, password = create_user(username=username, email=email, role=role)
    resp = client.post(
        "/api/users/login",
        json={"username": user.username, "password": password},
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}, user


def _make_festival(client, headers, name="Fest"):
    resp = client.post("/api/festivals/", json={"name": name}, headers=headers)
    assert resp.status_code == 201
    return resp.json()


def _enable(client, admin_headers, enabled=True):
    resp = client.put("/api/badges/settings", json={"enabled": enabled}, headers=admin_headers)
    assert resp.status_code == 200
    return resp.json()


class TestFeatureFlag:
    def test_status_defaults_disabled(self, client):
        resp = client.get("/api/badges/status")
        assert resp.status_code == 200
        assert resp.json()["enabled"] is False

    def test_list_gated_when_disabled(self, client, auth_headers):
        headers, _ = auth_headers
        resp = client.get("/api/badges/", headers=headers)
        assert resp.status_code == 403

    def test_admin_bypasses_gate(self, client, admin_headers):
        headers, _ = admin_headers
        resp = client.get("/api/badges/", headers=headers)
        assert resp.status_code == 200

    def test_only_admin_can_toggle(self, client, auth_headers, admin_headers):
        headers, _ = auth_headers
        resp = client.put("/api/badges/settings", json={"enabled": True}, headers=headers)
        assert resp.status_code == 403
        admin_h, _ = admin_headers
        _enable(client, admin_h, True)
        assert client.get("/api/badges/status").json()["enabled"] is True


class TestBadgeCrud:
    def test_admin_crud(self, client, admin_headers):
        admin_h, _ = admin_headers
        _enable(client, admin_h, True)
        created = client.post(
            "/api/badges/",
            json={"name": "Veterano", "category": "veteran", "conditions": {"type": "veteran", "min_festivals": 2}},
            headers=admin_h,
        )
        assert created.status_code == 201
        badge_id = created.json()["id"]

        bad = client.post("/api/badges/", json={"name": "X", "conditions": {"type": "nope"}}, headers=admin_h)
        assert bad.status_code == 422

        updated = client.put(f"/api/badges/{badge_id}", json={"description": "Hola"}, headers=admin_h)
        assert updated.status_code == 200

        deleted = client.delete(f"/api/badges/{badge_id}", headers=admin_h)
        assert deleted.status_code == 200

    def test_non_admin_cannot_create(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        _enable(client, admin_h, True)
        headers, _ = auth_headers
        resp = client.post("/api/badges/", json={"name": "Hack"}, headers=headers)
        assert resp.status_code == 403


class TestBadgeImage:
    def test_upload_svg(self, client, admin_headers):
        admin_h, _ = admin_headers
        badge = client.post("/api/badges/", json={"name": "SVG"}, headers=admin_h).json()
        resp = client.post(
            f"/api/badges/{badge['id']}/image",
            files={"file": ("badge.svg", b'<svg xmlns="http://www.w3.org/2000/svg"></svg>', "image/svg+xml")},
            headers=admin_h,
        )
        assert resp.status_code == 200
        assert resp.json()["image_url"].endswith(".svg")

    def test_upload_rejects_exe(self, client, admin_headers):
        admin_h, _ = admin_headers
        badge = client.post("/api/badges/", json={"name": "SVG2"}, headers=admin_h).json()
        resp = client.post(
            f"/api/badges/{badge['id']}/image",
            files={"file": ("evil.exe", b"MZ...", "application/octet-stream")},
            headers=admin_h,
        )
        assert resp.status_code == 400

    def test_upload_rejects_fake_svg(self, client, admin_headers):
        admin_h, _ = admin_headers
        badge = client.post("/api/badges/", json={"name": "SVG3"}, headers=admin_h).json()
        resp = client.post(
            f"/api/badges/{badge['id']}/image",
            files={"file": ("fake.svg", b"not xml at all", "image/svg+xml")},
            headers=admin_h,
        )
        assert resp.status_code == 400


class TestAssign:
    def test_platform_badge_admin_only(self, client, auth_headers, admin_headers, create_user):
        admin_h, _ = admin_headers
        _enable(client, admin_h, True)
        badge = client.post("/api/badges/", json={"name": "Top"}, headers=admin_h).json()
        headers, user = auth_headers
        resp = client.post(f"/api/badges/{badge['id']}/assign", json={"target_user_id": user.id}, headers=headers)
        assert resp.status_code == 403
        ok = client.post(
            f"/api/badges/{badge['id']}/assign",
            json={"target_user_id": user.id, "reason": "Great work"},
            headers=admin_h,
        )
        assert ok.status_code == 201
        listed = client.get(f"/api/users/{user.id}/badges/", headers=headers)
        assert listed.json()["total"] == 1

    def test_veteran_condition_enforced(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        _enable(client, admin_h, True)
        headers, user = auth_headers
        badge = client.post(
            "/api/badges/",
            json={"name": "Vet", "conditions": {"type": "veteran", "min_festivals": 2}},
            headers=admin_h,
        ).json()
        denied = client.post(f"/api/badges/{badge['id']}/assign", json={"target_user_id": user.id}, headers=admin_h)
        assert denied.status_code == 422
        _make_festival(client, headers, "F1")
        _make_festival(client, headers, "F2")
        eligible = client.get(f"/api/badges/{badge['id']}/eligibility?user_id={user.id}", headers=headers)
        assert eligible.json()["eligible"] is True
        ok = client.post(f"/api/badges/{badge['id']}/assign", json={"target_user_id": user.id}, headers=admin_h)
        assert ok.status_code == 201

    def test_festival_manager_grants_festival_badge(self, client, auth_headers, admin_headers, create_user):
        admin_h, _ = admin_headers
        _enable(client, admin_h, True)
        headers, _ = auth_headers
        fest = _make_festival(client, headers, "FM")
        badge = client.post(
            "/api/badges/",
            json={"name": "Org24", "scope": "festival", "festival_id": fest["id"], "category": "role"},
            headers=admin_h,
        ).json()
        other_h, other = _login(client, create_user, "cand", "cand@example.com")
        ok = client.post(
            f"/api/badges/{badge['id']}/assign",
            json={"target_user_id": other.id, "reason": "Organizer"},
            headers=headers,
        )
        assert ok.status_code == 201
        denied = client.post(f"/api/badges/{badge['id']}/assign", json={"target_user_id": other.id}, headers=other_h)
        assert denied.status_code == 403

    def test_badge_to_festival_profile(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        _enable(client, admin_h, True)
        headers, _ = auth_headers
        fest = _make_festival(client, headers, "FP")
        badge = client.post("/api/badges/", json={"name": "Sede"}, headers=admin_h).json()
        ok = client.post(f"/api/badges/{badge['id']}/assign", json={"target_festival_id": fest["id"]}, headers=admin_h)
        assert ok.status_code == 201
        listed = client.get(f"/api/festivals/{fest['id']}/badges/")
        assert listed.json()["total"] == 1

    def test_needs_exactly_one_target(self, client, auth_headers, admin_headers):
        admin_h, _ = admin_headers
        _enable(client, admin_h, True)
        headers, user = auth_headers
        badge = client.post("/api/badges/", json={"name": "T"}, headers=admin_h).json()
        resp = client.post(
            f"/api/badges/{badge['id']}/assign",
            json={"target_user_id": user.id, "target_festival_id": 1},
            headers=admin_h,
        )
        assert resp.status_code == 422
