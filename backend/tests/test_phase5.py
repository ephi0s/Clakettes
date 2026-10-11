"""Tests for user-festival association, file upload, and search endpoints."""


class TestUserFestival:
    """Tests for POST/DELETE /api/festivals/{id}/join|leave."""

    def test_join_festival(self, client, auth_headers, db_session):
        headers, user = auth_headers
        from app.models.festival import Festival

        fest = Festival(name="JoinFest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        response = client.post(f"/api/festivals/{fest.id}/join", headers=headers)
        assert response.status_code == 200
        assert "Joined" in response.json()["message"]

    def test_join_festival_duplicate(self, client, auth_headers, db_session):
        headers, user = auth_headers
        from app.models.festival import Festival

        fest = Festival(name="DupFest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        client.post(f"/api/festivals/{fest.id}/join", headers=headers)
        response = client.post(f"/api/festivals/{fest.id}/join", headers=headers)
        assert response.status_code == 409

    def test_leave_festival(self, client, auth_headers, db_session):
        headers, user = auth_headers
        from app.models.festival import Festival

        fest = Festival(name="LeaveFest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        client.post(f"/api/festivals/{fest.id}/join", headers=headers)
        response = client.delete(f"/api/festivals/{fest.id}/leave", headers=headers)
        assert response.status_code == 200

    def test_leave_festival_not_member(self, client, auth_headers, db_session):
        headers, user = auth_headers
        from app.models.festival import Festival

        fest = Festival(name="NotMember", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        response = client.delete(f"/api/festivals/{fest.id}/leave", headers=headers)
        assert response.status_code == 404

    def test_list_festival_members(self, client, auth_headers, db_session):
        headers, user = auth_headers
        from app.models.festival import Festival

        fest = Festival(name="MembersFest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        client.post(f"/api/festivals/{fest.id}/join", headers=headers)
        response = client.get(f"/api/festivals/{fest.id}/members", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["members"][0]["username"] == user.username

    def test_list_festival_members_requires_auth(self, client, auth_headers, db_session):
        headers, user = auth_headers
        from app.models.festival import Festival

        fest = Festival(name="MembersAuth", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        response = client.get(f"/api/festivals/{fest.id}/members")
        assert response.status_code == 401

    def test_list_user_festivals(self, client, auth_headers, db_session):
        headers, user = auth_headers
        from app.models.festival import Festival

        fest = Festival(name="UserFest", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        client.post(f"/api/festivals/{fest.id}/join", headers=headers)
        response = client.get(f"/api/festivals/user/{user.id}/festivals", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["festivals"][0]["name"] == "UserFest"

    def test_list_user_festivals_requires_auth(self, client, auth_headers, db_session):
        headers, user = auth_headers
        from app.models.festival import Festival

        fest = Festival(name="UserFestAuth", is_active=True)
        db_session.add(fest)
        db_session.commit()
        db_session.refresh(fest)
        response = client.get(f"/api/festivals/user/{user.id}/festivals")
        assert response.status_code == 401


class TestSearch:
    """Tests for GET /api/search/."""

    def test_search_festivals(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        from app.models.festival import Festival

        db_session.add(Festival(name="Sundance Film Fest", location="Utah"))
        db_session.commit()
        response = client.get("/api/search/?q=sundance&type=festivals", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert data["results"]["festivals"][0]["name"] == "Sundance Film Fest"

    def test_search_users_public_only(self, client, auth_headers, db_session):
        headers, user = auth_headers
        user.is_public = True
        db_session.commit()
        response = client.get(f"/api/search/?q={user.username}&type=users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_search_users_excludes_private_by_default(self, client, auth_headers, db_session):
        headers, user = auth_headers
        assert user.is_public is False
        response = client.get(f"/api/search/?q={user.username}&type=users", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] == 0

    def test_search_all(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        from app.models.festival import Festival

        db_session.add(Festival(name="SearchAll", location="NYC"))
        db_session.commit()
        response = client.get("/api/search/?q=SearchAll", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_search_empty_query_fails(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/search/?q=", headers=headers)
        assert response.status_code == 422


class TestUpload:
    """Tests for POST /api/uploads/*."""

    def test_upload_avatar(self, client, auth_headers):
        headers, _ = auth_headers
        import io

        from PIL import Image

        buf = io.BytesIO()
        Image.new("RGB", (8, 8), "red").save(buf, format="PNG")
        response = client.post(
            "/api/uploads/avatar",
            headers=headers,
            files={"file": ("test.png", buf.getvalue(), "image/png")},
        )
        assert response.status_code == 200
        assert "url" in response.json()

    def test_upload_rejects_bad_type(self, client, auth_headers):
        headers, _ = auth_headers
        import io

        response = client.post(
            "/api/uploads/avatar",
            headers=headers,
            files={"file": ("test.exe", io.BytesIO(b"bad"), "application/octet-stream")},
        )
        assert response.status_code == 400

    def test_upload_requires_auth(self, client):
        import io

        response = client.post(
            "/api/uploads/avatar",
            files={"file": ("test.png", io.BytesIO(b"fake"), "image/png")},
        )
        assert response.status_code == 401
