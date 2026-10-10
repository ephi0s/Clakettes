class TestLocationBadge:
    def _create_location(self, client, headers):
        resp = client.post(
            "/api/locations/",
            json={
                "name": "Badge Location",
                "latitude": 40.0,
                "longitude": -3.0,
            },
            headers=headers,
        )
        return resp.json()["id"]

    def test_admin_set_badge(self, client, admin_headers):
        headers, _ = admin_headers
        loc_id = self._create_location(client, headers)
        resp = client.put(f"/api/locations/{loc_id}/badge?badge=featured", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["badge"] == "featured"

    def test_normal_user_cannot_set_badge(self, client, auth_headers):
        headers, _ = auth_headers
        loc_id = self._create_location(client, headers)
        resp = client.put(f"/api/locations/{loc_id}/badge?badge=featured", headers=headers)
        assert resp.status_code == 403

    def test_get_filters_by_badge(self, client, admin_headers):
        headers, _ = admin_headers
        loc_id = self._create_location(client, headers)
        client.put(f"/api/locations/{loc_id}/badge?badge=mandatory", headers=headers)
        resp = client.get("/api/locations/?badge=mandatory")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == loc_id

    def test_get_filters_by_badge_no_match(self, client, admin_headers):
        headers, _ = admin_headers
        self._create_location(client, headers)
        resp = client.get("/api/locations/?badge=suggested")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_badge_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        resp = client.put("/api/locations/9999/badge?badge=featured", headers=headers)
        assert resp.status_code == 404


class TestLocationAddedBy:
    def test_post_grabs_creator(self, client, auth_headers):
        headers, user = auth_headers
        resp = client.post(
            "/api/locations/",
            json={
                "name": "Created Location",
                "latitude": 40.0,
                "longitude": -3.0,
            },
            headers=headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["added_by"] == user.id

    def test_post_requires_auth(self, client):
        resp = client.post(
            "/api/locations/",
            json={
                "name": "No Auth",
                "latitude": 40.0,
                "longitude": -3.0,
            },
        )
        assert resp.status_code == 401
