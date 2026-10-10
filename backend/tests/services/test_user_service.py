import pytest
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate


@pytest.fixture
def service():
    return UserService()


class TestCreate:
    def test_creates_user_with_hashed_password(self, db_session, service):
        user_in = UserCreate(
            username="newuser",
            email="new@example.com",
            password="MyPassword123",
            role="user",
        )
        user = service.create(db_session, user_in)
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.password_hash != "MyPassword123"
        assert user.password_hash.startswith("$2b$")

    def test_creates_with_all_fields(self, db_session, service):
        user_in = UserCreate(
            username="fulluser",
            email="full@example.com",
            password="Secret1!",
            full_name="Full Name",
            role="admin",
            bio="A bio",
            avatar_url="http://example.com/avatar.png",
            is_public=True,
            is_public_email=False,
            is_public_bio=False,
            is_public_location=False,
            latitude=41.3874,
            longitude=2.1686,
        )
        user = service.create(db_session, user_in)
        assert user.full_name == "Full Name"
        assert user.role == "admin"
        assert user.bio == "A bio"
        assert user.avatar_url == "http://example.com/avatar.png"
        assert user.is_public is True
        assert user.is_public_email is False
        assert user.is_public_bio is False
        assert user.is_public_location is False
        assert user.latitude == 41.3874
        assert user.longitude == 2.1686


class TestGetByUsername:
    def test_found(self, db_session, service, create_user):
        create_user(username="jdoe", email="jdoe@example.com")
        user = service.get_by_username(db_session, "jdoe")
        assert user is not None
        assert user.username == "jdoe"

    def test_not_found(self, db_session, service):
        user = service.get_by_username(db_session, "nonexistent")
        assert user is None


class TestGetByEmail:
    def test_found(self, db_session, service, create_user):
        create_user(username="u1", email="findme@example.com")
        user = service.get_by_email(db_session, "findme@example.com")
        assert user is not None
        assert user.email == "findme@example.com"

    def test_not_found(self, db_session, service):
        user = service.get_by_email(db_session, "missing@example.com")
        assert user is None


class TestGetMultiPaginated:
    def test_filters_by_is_active(self, db_session, service, create_user):
        create_user(username="active1", email="a1@test.com", role="user")
        create_user(username="active2", email="a2@test.com", role="user")
        inactive = create_user(username="inactive1", email="i1@test.com", role="user")
        inactive.is_active = False
        db_session.commit()

        result = service.get_multi_paginated(db_session, is_active=True)
        assert len(result["items"]) == 2

        result = service.get_multi_paginated(db_session, is_active=False)
        assert len(result["items"]) == 1

    def test_filters_by_role(self, db_session, service, create_user):
        create_user(username="org1", email="org1@test.com", role="organizer")
        create_user(username="org2", email="org2@test.com", role="organizer")
        create_user(username="usr1", email="usr1@test.com", role="user")

        result = service.get_multi_paginated(db_session, role="organizer")
        assert len(result["items"]) == 2

        result = service.get_multi_paginated(db_session, role="user")
        assert len(result["items"]) == 1

    def test_combines_filters(self, db_session, service, create_user):
        create_user(username="a", email="a@test.com", role="user")
        create_user(username="b", email="b@test.com", role="user")
        u = create_user(username="c", email="c@test.com", role="admin")
        u.is_active = False
        db_session.commit()
        create_user(username="d", email="d@test.com", role="admin")

        result = service.get_multi_paginated(db_session, is_active=True, role="admin")
        assert len(result["items"]) == 1
        assert result["items"][0].username == "d"

    def test_page_and_size(self, db_session, service, create_user):
        for i in range(25):
            create_user(username=f"user{i}", email=f"user{i}@example.com")

        page1 = service.get_multi_paginated(db_session, page=1, size=10)
        assert len(page1["items"]) == 10
        assert page1["total"] == 25
        assert page1["page"] == 1
        assert page1["pages"] == 3

        page3 = service.get_multi_paginated(db_session, page=3, size=10)
        assert len(page3["items"]) == 5


class TestGetPublicUsers:
    def test_returns_only_public_users(self, db_session, service, create_user):
        create_user(username="pub1", email="pub1@test.com")
        create_user(username="pub2", email="pub2@test.com")
        private = create_user(username="priv1", email="priv1@test.com")
        private.is_public = False
        db_session.commit()

        result = service.get_public_users(db_session)
        assert len(result) == 2
        usernames = {u["username"] for u in result}
        assert "pub1" in usernames
        assert "pub2" in usernames
        assert "priv1" not in usernames

    def test_respects_privacy_flags(self, db_session, service, create_user):
        user = create_user(username="user1", email="user1@example.com")
        user.full_name = "Visible Name"
        user.bio = "Public bio"
        user.latitude = 10.0
        user.longitude = 20.0
        user.is_public_email = True
        user.is_public_bio = True
        user.is_public_location = True
        db_session.commit()

        result = service.get_public_users(db_session)
        data = result[0]
        assert data["email"] == "user1@example.com"
        assert data["bio"] == "Public bio"
        assert data["latitude"] == 10.0
        assert data["longitude"] == 20.0

    def test_hides_fields_when_flags_false(self, db_session, service, create_user):
        user = create_user(username="user2", email="user2@example.com")
        user.full_name = "Hidden Name"
        user.bio = "Secret bio"
        user.latitude = 30.0
        user.longitude = 40.0
        user.is_public_email = False
        user.is_public_bio = False
        user.is_public_location = False
        db_session.commit()

        result = service.get_public_users(db_session)
        data = result[0]
        assert "email" not in data
        assert "bio" not in data
        assert "latitude" not in data
        assert "longitude" not in data

    def test_pagination(self, db_session, service, create_user):
        for i in range(55):
            create_user(username=f"pub{i}", email=f"pub{i}@test.com")

        page1 = service.get_public_users(db_session, page=1, size=50)
        assert len(page1) == 50

        page2 = service.get_public_users(db_session, page=2, size=50)
        assert len(page2) == 5


class TestToPublicResponse:
    def test_returns_id_username_role_avatar_active_created(self, db_session, service, create_user):
        user = create_user()
        data = service.to_public_response(user)
        assert data["id"] == user.id
        assert data["username"] == "testuser"
        assert data["role"] == "user"
        assert data["avatar_url"] == user.avatar_url
        assert data["is_active"] is True
        assert data["created_at"] == user.created_at

    def test_full_name_when_public(self, db_session, service, create_user):
        user = create_user()
        user.full_name = "Test User"
        user.is_public = True
        db_session.commit()
        data = service.to_public_response(user)
        assert data["full_name"] == "Test User"

    def test_full_name_none_when_not_public(self, db_session, service, create_user):
        user = create_user()
        user.full_name = "Test User"
        user.is_public = False
        db_session.commit()
        data = service.to_public_response(user)
        assert data["full_name"] is None

    def test_email_included_when_is_public_email(self, db_session, service, create_user):
        user = create_user()
        user.is_public_email = True
        db_session.commit()
        data = service.to_public_response(user)
        assert data.get("email") == "test@example.com"

    def test_email_excluded_when_not_public_email(self, db_session, service, create_user):
        user = create_user()
        user.is_public_email = False
        db_session.commit()
        data = service.to_public_response(user)
        assert "email" not in data

    def test_bio_included_when_is_public_bio(self, db_session, service, create_user):
        user = create_user()
        user.bio = "My bio"
        user.is_public_bio = True
        db_session.commit()
        data = service.to_public_response(user)
        assert data.get("bio") == "My bio"

    def test_bio_excluded_when_not_public_bio(self, db_session, service, create_user):
        user = create_user()
        user.bio = "Secret bio"
        user.is_public_bio = False
        db_session.commit()
        data = service.to_public_response(user)
        assert "bio" not in data

    def test_location_included_when_is_public_location(self, db_session, service, create_user):
        user = create_user()
        user.latitude = 10.0
        user.longitude = 20.0
        user.is_public_location = True
        db_session.commit()
        data = service.to_public_response(user)
        assert data.get("latitude") == 10.0
        assert data.get("longitude") == 20.0

    def test_location_excluded_when_not_public_location(self, db_session, service, create_user):
        user = create_user()
        user.latitude = 10.0
        user.longitude = 20.0
        user.is_public_location = False
        db_session.commit()
        data = service.to_public_response(user)
        assert "latitude" not in data
        assert "longitude" not in data


class TestAuthenticate:
    def test_success(self, db_session, service, create_user):
        create_user(username="authuser", password="CorrectPwd1")
        user = service.authenticate(db_session, "authuser", "CorrectPwd1")
        assert user is not None
        assert user.username == "authuser"

    def test_wrong_password(self, db_session, service, create_user):
        create_user(username="authuser2", password="CorrectPwd1")
        user = service.authenticate(db_session, "authuser2", "WrongPwd")
        assert user is None

    def test_non_existent_user(self, db_session, service):
        user = service.authenticate(db_session, "ghost", "AnyPass1")
        assert user is None


class TestUpdate:
    def test_updates_fields(self, db_session, service, create_user):
        user = create_user(username="update_me", email="old@example.com")
        update = UserUpdate(username="updated", email="new@example.com", full_name="Updated Name")
        result = service.update(db_session, user.id, update)
        assert result is not None
        assert result.username == "updated"
        assert result.email == "new@example.com"
        assert result.full_name == "Updated Name"

    def test_updates_password_rehashes(self, db_session, service, create_user):
        user = create_user(username="passuser", password="OldPass1")
        old_hash = user.password_hash
        update = UserUpdate(password="NewPass1")
        result = service.update(db_session, user.id, update)
        assert result.password_hash != old_hash
        assert result.password_hash.startswith("$2b$")

    def test_returns_none_for_non_existent(self, db_session, service):
        update = UserUpdate(username="nope")
        result = service.update(db_session, 9999, update)
        assert result is None
