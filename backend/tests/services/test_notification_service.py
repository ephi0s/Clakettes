from app.services.notification_service import NotificationService

service = NotificationService()


class TestCreateNotification:
    def test_creates_with_all_fields(self, db_session, create_user):
        user = create_user()
        notif = service.create_notification(
            db_session,
            user_id=user.id,
            title="Profile Updated",
            message="Your profile has been updated.",
            notification_type="profile_update",
            related_user_id=None,
        )
        assert notif.id is not None
        assert notif.user_id == user.id
        assert notif.title == "Profile Updated"
        assert notif.message == "Your profile has been updated."
        assert notif.notification_type == "profile_update"
        assert notif.is_read is False
        assert notif.related_user_id is None

    def test_creates_with_minimal_fields(self, db_session, create_user):
        user = create_user()
        notif = service.create_notification(
            db_session,
            user_id=user.id,
            title="Test",
            message="Hello",
        )
        assert notif.id is not None
        assert notif.user_id == user.id
        assert notif.title == "Test"
        assert notif.message == "Hello"
        assert notif.notification_type == "profile_update"
        assert notif.is_read is False
        assert notif.related_user_id is None


class TestGetMultiPaginated:
    def test_paginates(self, db_session, create_user):
        user = create_user()
        for i in range(5):
            service.create_notification(db_session, user.id, f"Title {i}", f"Msg {i}")

        page1 = service.get_multi_paginated(db_session, page=1, size=2)
        assert len(page1["items"]) == 2
        assert page1["total"] == 5
        assert page1["page"] == 1
        assert page1["pages"] == 3

        page2 = service.get_multi_paginated(db_session, page=2, size=2)
        assert len(page2["items"]) == 2

        page3 = service.get_multi_paginated(db_session, page=3, size=2)
        assert len(page3["items"]) == 1

    def test_filters_by_user_id(self, db_session, create_user):
        user1 = create_user(username="user1", email="u1@test.com")
        user2 = create_user(username="user2", email="u2@test.com")
        service.create_notification(db_session, user1.id, "A", "a")
        service.create_notification(db_session, user1.id, "B", "b")
        service.create_notification(db_session, user2.id, "C", "c")

        result = service.get_multi_paginated(db_session, user_id=user1.id)
        assert len(result["items"]) == 2

        result = service.get_multi_paginated(db_session, user_id=user2.id)
        assert len(result["items"]) == 1

    def test_filters_by_is_read(self, db_session, create_user):
        user = create_user()
        n1 = service.create_notification(db_session, user.id, "A", "a")
        n2 = service.create_notification(db_session, user.id, "B", "b")
        service.mark_as_read(db_session, n1.id, user.id)

        unread = service.get_multi_paginated(db_session, is_read=False, user_id=user.id)
        assert len(unread["items"]) == 1
        assert unread["items"][0].id == n2.id

        read = service.get_multi_paginated(db_session, is_read=True, user_id=user.id)
        assert len(read["items"]) == 1
        assert read["items"][0].id == n1.id


class TestGetUnreadCount:
    def test_returns_correct_count(self, db_session, create_user):
        user = create_user()
        service.create_notification(db_session, user.id, "A", "a")
        service.create_notification(db_session, user.id, "B", "b")

        assert service.get_unread_count(db_session, user.id) == 2

    def test_returns_zero_when_all_read(self, db_session, create_user):
        user = create_user()
        n1 = service.create_notification(db_session, user.id, "A", "a")
        n2 = service.create_notification(db_session, user.id, "B", "b")
        service.mark_as_read(db_session, n1.id, user.id)
        service.mark_as_read(db_session, n2.id, user.id)

        assert service.get_unread_count(db_session, user.id) == 0


class TestMarkAsRead:
    def test_marks_notification_as_read(self, db_session, create_user):
        user = create_user()
        notif = service.create_notification(db_session, user.id, "A", "a")
        assert notif.is_read is False

        updated = service.mark_as_read(db_session, notif.id, user.id)
        assert updated is not None
        assert updated.is_read is True

    def test_returns_none_for_wrong_user_id(self, db_session, create_user):
        user1 = create_user(username="u1", email="u1@test.com")
        user2 = create_user(username="u2", email="u2@test.com")
        notif = service.create_notification(db_session, user1.id, "A", "a")

        result = service.mark_as_read(db_session, notif.id, user2.id)
        assert result is None

    def test_returns_none_for_non_existent(self, db_session, create_user):
        user = create_user()
        result = service.mark_as_read(db_session, 9999, user.id)
        assert result is None


class TestMarkAllAsRead:
    def test_marks_all_unread_for_user(self, db_session, create_user):
        user = create_user()
        service.create_notification(db_session, user.id, "A", "a")
        service.create_notification(db_session, user.id, "B", "b")

        count = service.mark_all_as_read(db_session, user.id)
        assert count == 2
        assert service.get_unread_count(db_session, user.id) == 0

    def test_returns_count(self, db_session, create_user):
        user = create_user()
        service.create_notification(db_session, user.id, "A", "a")
        service.create_notification(db_session, user.id, "B", "b")
        service.create_notification(db_session, user.id, "C", "c")

        count = service.mark_all_as_read(db_session, user.id)
        assert count == 3

    def test_does_not_mark_other_users_notifications(self, db_session, create_user):
        user1 = create_user(username="u1", email="u1@test.com")
        user2 = create_user(username="u2", email="u2@test.com")
        service.create_notification(db_session, user1.id, "A", "a")
        service.create_notification(db_session, user1.id, "B", "b")
        service.create_notification(db_session, user2.id, "C", "c")

        count = service.mark_all_as_read(db_session, user1.id)
        assert count == 2
        assert service.get_unread_count(db_session, user1.id) == 0
        assert service.get_unread_count(db_session, user2.id) == 1
