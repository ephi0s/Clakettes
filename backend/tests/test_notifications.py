"""Tests for notification endpoints."""

from app.models.notification import Notification


class TestListNotifications:
    """Tests for GET /api/notifications/."""

    def test_list_empty(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/notifications/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_with_notifications(self, client, auth_headers, db_session):
        headers, user = auth_headers
        for i in range(3):
            db_session.add(
                Notification(
                    user_id=user.id,
                    title=f"Notif {i}",
                    message=f"Message {i}",
                    notification_type="profile_update",
                )
            )
        db_session.commit()
        response = client.get("/api/notifications/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_list_requires_auth(self, client):
        response = client.get("/api/notifications/")
        assert response.status_code == 401


class TestUnreadCount:
    """Tests for GET /api/notifications/unread-count."""

    def test_unread_count_zero(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.get("/api/notifications/unread-count", headers=headers)
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_unread_count_with_unread(self, client, auth_headers, db_session):
        headers, user = auth_headers
        db_session.add(
            Notification(
                user_id=user.id,
                title="Unread",
                message="Test",
                notification_type="profile_update",
            )
        )
        db_session.commit()
        response = client.get("/api/notifications/unread-count", headers=headers)
        assert response.status_code == 200
        assert response.json()["count"] == 1

    def test_unread_count_after_read(self, client, auth_headers, db_session):
        headers, user = auth_headers
        notif = Notification(
            user_id=user.id,
            title="Read me",
            message="Will be read",
            notification_type="profile_update",
        )
        db_session.add(notif)
        db_session.commit()
        notif.is_read = True
        db_session.commit()
        response = client.get("/api/notifications/unread-count", headers=headers)
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_unread_count_requires_auth(self, client):
        response = client.get("/api/notifications/unread-count")
        assert response.status_code == 401


class TestMarkRead:
    """Tests for PUT /api/notifications/{id}/read."""

    def test_mark_read_success(self, client, auth_headers, db_session):
        headers, user = auth_headers
        notif = Notification(
            user_id=user.id,
            title="Mark read",
            message="Test",
            notification_type="profile_update",
        )
        db_session.add(notif)
        db_session.commit()
        db_session.refresh(notif)
        response = client.put(f"/api/notifications/{notif.id}/read", headers=headers)
        assert response.status_code == 200
        assert response.json()["is_read"] is True

    def test_mark_read_not_found(self, client, auth_headers):
        headers, _ = auth_headers
        response = client.put("/api/notifications/9999/read", headers=headers)
        assert response.status_code == 404

    def test_mark_read_other_user_not_found(self, client, auth_headers, db_session, create_user):
        headers, _ = auth_headers
        other, _ = create_user(username="other", email="other@example.com")
        notif = Notification(
            user_id=other.id,
            title="Other's notif",
            message="Not mine",
            notification_type="profile_update",
        )
        db_session.add(notif)
        db_session.commit()
        response = client.put(f"/api/notifications/{notif.id}/read", headers=headers)
        assert response.status_code == 404


class TestMarkAllRead:
    """Tests for PUT /api/notifications/read-all."""

    def test_mark_all_read(self, client, auth_headers, db_session):
        headers, user = auth_headers
        for i in range(3):
            db_session.add(
                Notification(
                    user_id=user.id,
                    title=f"N{i}",
                    message=f"M{i}",
                    notification_type="profile_update",
                )
            )
        db_session.commit()
        response = client.put("/api/notifications/read-all", headers=headers)
        assert response.status_code == 200
        assert response.json()["marked"] == 3
        check = client.get("/api/notifications/unread-count", headers=headers)
        assert check.json()["count"] == 0

    def test_mark_all_read_requires_auth(self, client):
        response = client.put("/api/notifications/read-all")
        assert response.status_code == 401


class TestDeleteNotification:
    """Tests for DELETE /api/notifications/{id}."""

    def test_delete_success(self, client, auth_headers, db_session):
        headers, user = auth_headers
        notif = Notification(
            user_id=user.id,
            title="Delete me",
            message="Test",
            notification_type="profile_update",
        )
        db_session.add(notif)
        db_session.commit()
        db_session.refresh(notif)
        response = client.delete(f"/api/notifications/{notif.id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Notification deleted"
        check = client.get("/api/notifications/", headers=headers)
        assert check.json()["total"] == 0

    def test_delete_other_user_not_found(self, client, auth_headers, db_session, create_user):
        headers, _ = auth_headers
        other, _ = create_user(username="other2", email="other2@example.com")
        notif = Notification(
            user_id=other.id,
            title="Not mine",
            message="Other's notification",
            notification_type="profile_update",
        )
        db_session.add(notif)
        db_session.commit()
        response = client.delete(f"/api/notifications/{notif.id}", headers=headers)
        assert response.status_code == 404

    def test_delete_requires_auth(self, client):
        response = client.delete("/api/notifications/1")
        assert response.status_code == 401
