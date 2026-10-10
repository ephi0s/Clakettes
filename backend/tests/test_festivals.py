"""Tests for festival CRUD endpoints."""


class TestListFestivals:
    """Tests for GET /api/festivals/."""

    def test_list_empty(self, client):
        response = client.get("/api/festivals/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_with_festivals(self, client, auth_headers):
        headers, _ = auth_headers
        client.post("/api/festivals/", json={"name": "Fest 1"}, headers=headers)
        client.post("/api/festivals/", json={"name": "Fest 2"}, headers=headers)
        response = client.get("/api/festivals/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2


class TestCreateFestival:
    """Tests for POST /api/festivals/."""

    def test_create_success(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.post(
            "/api/festivals/",
            json={
                "name": "Sundance",
                "description": "Film festival",
                "location": "Utah",
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Sundance"
        assert data["is_active"] is True

    def test_create_requires_auth(self, client):
        response = client.post("/api/festivals/", json={"name": "No Auth"})
        assert response.status_code == 401


class TestGetFestival:
    """Tests for GET /api/festivals/{id}."""

    def test_get_success(self, client, auth_headers):
        headers, user = auth_headers
        create_resp = client.post("/api/festivals/", json={"name": "Test"}, headers=headers)
        fest_id = create_resp.json()["id"]
        response = client.get(f"/api/festivals/{fest_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Test"

    def test_get_not_found(self, client):
        response = client.get("/api/festivals/9999")
        assert response.status_code == 404


class TestUpdateFestival:
    """Tests for PUT /api/festivals/{id}."""

    def test_update_success(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Old"}, headers=headers)
        fest_id = create_resp.json()["id"]
        response = client.put(f"/api/festivals/{fest_id}", json={"name": "New"}, headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "New"

    def test_update_requires_auth(self, client, auth_headers):
        headers, _ = auth_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=headers)
        fest_id = create_resp.json()["id"]
        response = client.put(f"/api/festivals/{fest_id}", json={"name": "Hacked"})
        assert response.status_code == 401


class TestDeleteFestival:
    """Tests for DELETE /api/festivals/{id}."""

    def test_delete_success(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Doomed"}, headers=headers)
        fest_id = create_resp.json()["id"]
        response = client.delete(f"/api/festivals/{fest_id}", headers=headers)
        assert response.status_code == 200
        get_resp = client.get(f"/api/festivals/{fest_id}")
        assert get_resp.status_code == 404

    def test_delete_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=headers)
        fest_id = create_resp.json()["id"]
        response = client.delete(f"/api/festivals/{fest_id}")
        assert response.status_code == 401

    def test_delete_not_found(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.delete("/api/festivals/9999", headers=headers)
        assert response.status_code == 404


class TestFestivalLocations:
    """Tests for festival-location association endpoints."""

    def _create_location(self, client, headers, name="Lugar"):
        response = client.post(
            "/api/locations/",
            json={"name": name, "latitude": 40.0, "longitude": -3.7},
            headers=headers,
        )
        return response.json()["id"]

    def test_list_empty(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=headers)
        fest_id = create_resp.json()["id"]
        response = client.get(f"/api/festivals/{fest_id}/locations")
        assert response.status_code == 200
        assert response.json() == []

    def test_add_and_list(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=headers)
        fest_id = create_resp.json()["id"]
        loc_id = self._create_location(client, headers)

        add_resp = client.post(f"/api/festivals/{fest_id}/locations", json={"location_id": loc_id}, headers=headers)
        assert add_resp.status_code == 201
        assert add_resp.json()["id"] == loc_id

        list_resp = client.get(f"/api/festivals/{fest_id}/locations")
        assert list_resp.status_code == 200
        assert [loc["id"] for loc in list_resp.json()] == [loc_id]

    def test_add_duplicate_conflict(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=headers)
        fest_id = create_resp.json()["id"]
        loc_id = self._create_location(client, headers)
        client.post(f"/api/festivals/{fest_id}/locations", json={"location_id": loc_id}, headers=headers)
        dup = client.post(f"/api/festivals/{fest_id}/locations", json={"location_id": loc_id}, headers=headers)
        assert dup.status_code == 409

    def test_add_requires_auth(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=headers)
        fest_id = create_resp.json()["id"]
        loc_id = self._create_location(client, headers)
        response = client.post(f"/api/festivals/{fest_id}/locations", json={"location_id": loc_id})
        assert response.status_code == 401

    def test_add_forbidden_for_regular_user(self, client, auth_headers, admin_headers):
        admin, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=admin)
        fest_id = create_resp.json()["id"]
        loc_id = self._create_location(client, admin)
        user_headers, _ = auth_headers
        response = client.post(
            f"/api/festivals/{fest_id}/locations", json={"location_id": loc_id}, headers=user_headers
        )
        assert response.status_code == 403

    def test_remove(self, client, admin_headers):
        headers, _ = admin_headers
        create_resp = client.post("/api/festivals/", json={"name": "Fest"}, headers=headers)
        fest_id = create_resp.json()["id"]
        loc_id = self._create_location(client, headers)
        client.post(f"/api/festivals/{fest_id}/locations", json={"location_id": loc_id}, headers=headers)

        del_resp = client.delete(f"/api/festivals/{fest_id}/locations/{loc_id}", headers=headers)
        assert del_resp.status_code == 200

        list_resp = client.get(f"/api/festivals/{fest_id}/locations")
        assert list_resp.json() == []
