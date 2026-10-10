import pytest
from app.models.location import Location
from app.schemas.location_tag import LocationTagCreate
from app.schemas.shortfilm_location import ShortFilmLocationCreate, ShortFilmLocationUpdate
from app.schemas.location_relation import LocationRelationCreate
from app.services.location_tag_service import LocationTagService
from app.services.shortfilm_location_service import ShortFilmLocationService
from app.services.location_image_service import LocationImageService
from app.services.location_relation_service import LocationRelationService


@pytest.fixture
def create_location(db_session, create_user):
    user = create_user()
    loc = Location(
        name="Test Location",
        description="A place",
        address="123 Main St",
        latitude=40.0,
        longitude=-3.0,
        tags=["outdoor", "urban"],
        is_active=True,
        added_by=user.id,
    )
    db_session.add(loc)
    db_session.commit()
    db_session.refresh(loc)
    return loc


@pytest.fixture
def create_location_2(db_session, create_user):
    user = create_user(username="other", email="other@example.com")
    loc = Location(
        name="Nearby Location",
        description="Close by",
        address="125 Main St",
        latitude=40.001,
        longitude=-3.001,
        tags=["urban"],
        is_active=True,
        added_by=user.id,
    )
    db_session.add(loc)
    db_session.commit()
    db_session.refresh(loc)
    return loc


@pytest.fixture
def create_shortfilm(db_session, create_user):
    user = create_user(username="filmuser", email="film@example.com")
    from app.models.festival import Festival

    fest = Festival(name="Test Fest", location="City", is_active=True)
    db_session.add(fest)
    db_session.commit()
    db_session.refresh(fest)
    from app.models.shortfilm import ShortFilm

    film = ShortFilm(title="Test Film", description="Film", duration=90, festival_id=fest.id, user_id=user.id)
    db_session.add(film)
    db_session.commit()
    db_session.refresh(film)
    return film


class TestLocationTag:
    def test_create_tag_admin_approved(self, db_session, create_user):
        user = create_user(role="admin")
        svc = LocationTagService()
        tag = svc.create_tag(db_session, 1, LocationTagCreate(tag="outdoor"), user.id, is_admin=True)
        assert tag.status == "approved"

    def test_create_tag_user_proposed(self, db_session, create_user):
        user = create_user()
        svc = LocationTagService()
        tag = svc.create_tag(db_session, 1, LocationTagCreate(tag="urban"), user.id, is_admin=False)
        assert tag.status == "proposed"

    def test_get_by_location_excludes_revoked(self, db_session, create_user):
        user = create_user()
        svc = LocationTagService()
        svc.create_tag(db_session, 1, LocationTagCreate(tag="a"), user.id, is_admin=True)
        t2 = svc.create_tag(db_session, 1, LocationTagCreate(tag="b"), user.id, is_admin=True)
        svc.revoke_tag(db_session, t2.id)
        result = svc.get_by_location(db_session, 1)
        assert len(result) == 1
        assert result[0].tag == "a"

    def test_revoke_tag(self, db_session, create_user):
        user = create_user()
        svc = LocationTagService()
        tag = svc.create_tag(db_session, 1, LocationTagCreate(tag="x"), user.id, is_admin=True)
        revoked = svc.revoke_tag(db_session, tag.id)
        assert revoked.status == "revoked"

    def test_revoke_tag_not_found(self, db_session):
        svc = LocationTagService()
        assert svc.revoke_tag(db_session, 999) is None

    def test_approve_tag(self, db_session, create_user):
        user = create_user()
        svc = LocationTagService()
        tag = svc.create_tag(db_session, 1, LocationTagCreate(tag="y"), user.id, is_admin=False)
        assert tag.status == "proposed"
        approved = svc.approve_tag(db_session, tag.id)
        assert approved.status == "approved"


class TestShortFilmLocation:
    def test_create_link(self, db_session, create_location, create_shortfilm):
        svc = ShortFilmLocationService()
        data = ShortFilmLocationCreate(location_id=create_location.id)
        link = svc.create_link(db_session, create_shortfilm.id, data, create_location.added_by)
        assert link.shortfilm_id == create_shortfilm.id
        assert link.location_id == create_location.id

    def test_get_by_shortfilm(self, db_session, create_location, create_shortfilm):
        svc = ShortFilmLocationService()
        data = ShortFilmLocationCreate(location_id=create_location.id)
        svc.create_link(db_session, create_shortfilm.id, data, create_location.added_by)
        result = svc.get_by_shortfilm(db_session, create_shortfilm.id)
        assert len(result) == 1

    def test_update_link_keyframe(self, db_session, create_location, create_shortfilm):
        svc = ShortFilmLocationService()
        data = ShortFilmLocationCreate(location_id=create_location.id, start_time=0.0)
        link = svc.create_link(db_session, create_shortfilm.id, data, create_location.added_by)
        updated = svc.update_link(db_session, link.id, ShortFilmLocationUpdate(start_time=10.5, end_time=20.0))
        assert updated.start_time == 10.5
        assert updated.end_time == 20.0

    def test_delete_link(self, db_session, create_location, create_shortfilm):
        svc = ShortFilmLocationService()
        data = ShortFilmLocationCreate(location_id=create_location.id)
        link = svc.create_link(db_session, create_shortfilm.id, data, create_location.added_by)
        deleted = svc.delete(db_session, link.id)
        assert deleted is not None
        assert svc.get(db_session, link.id) is None

    def test_uniqueness_constraint(self, db_session, create_location, create_shortfilm):
        svc = ShortFilmLocationService()
        data = ShortFilmLocationCreate(location_id=create_location.id)
        svc.create_link(db_session, create_shortfilm.id, data, create_location.added_by)
        with pytest.raises(ValueError, match="already linked"):
            svc.create_link(db_session, create_shortfilm.id, data, create_location.added_by)


class TestLocationImage:
    def test_add_upload(self, db_session, create_user):
        user = create_user()
        svc = LocationImageService()
        img = svc.add_upload(db_session, 1, "http://img/test.jpg", user.id)
        assert img.source == "upload"
        assert img.url == "http://img/test.jpg"

    def test_add_url(self, db_session, create_user):
        user = create_user()
        svc = LocationImageService()
        img = svc.add_url(db_session, 1, "http://img/ext.png", user.id)
        assert img.source == "url"

    def test_remove_image(self, db_session, create_user):
        user = create_user()
        svc = LocationImageService()
        img = svc.add_url(db_session, 1, "http://img/to-delete.png", user.id)
        removed = svc.remove_image(db_session, img.id)
        assert removed is not None
        assert svc.get(db_session, img.id) is None

    def test_remove_image_not_found(self, db_session):
        svc = LocationImageService()
        assert svc.remove_image(db_session, 999) is None


class TestLocationRelation:
    def test_create_relation(self, db_session, create_location, create_location_2):
        svc = LocationRelationService()
        data = LocationRelationCreate(related_location_id=create_location_2.id, relation_type="proximity")
        rel = svc.create_relation(db_session, create_location.id, data, create_location.added_by)
        assert rel.location_id == create_location.id
        assert rel.related_location_id == create_location_2.id

    def test_remove_relation(self, db_session, create_location, create_location_2):
        svc = LocationRelationService()
        data = LocationRelationCreate(related_location_id=create_location_2.id, relation_type="proximity")
        rel = svc.create_relation(db_session, create_location.id, data, create_location.added_by)
        removed = svc.remove_relation(db_session, rel.id)
        assert removed is not None
        assert svc.get(db_session, rel.id) is None

    def test_duplicate_relation_raises(self, db_session, create_location, create_location_2):
        svc = LocationRelationService()
        data = LocationRelationCreate(related_location_id=create_location_2.id, relation_type="proximity")
        svc.create_relation(db_session, create_location.id, data, create_location.added_by)
        with pytest.raises(ValueError, match="already exists"):
            svc.create_relation(db_session, create_location.id, data, create_location.added_by)

    def test_suggest_proximity(self, db_session, create_location, create_location_2):
        svc = LocationRelationService()
        result = svc.suggest_proximity(db_session, create_location.id, radius_km=1.0)
        assert len(result) == 1
        assert result[0].related_location_id == create_location_2.id
        assert result[0].relation_type == "proximity"

    def test_suggest_proximity_too_far(self, db_session, create_location):
        loc_far = Location(name="Far Location", latitude=50.0, longitude=10.0, is_active=True)
        db_session.add(loc_far)
        db_session.commit()
        svc = LocationRelationService()
        result = svc.suggest_proximity(db_session, create_location.id, radius_km=1.0)
        assert len(result) == 0

    def test_suggest_by_tags(self, db_session, create_location, create_location_2):
        svc = LocationRelationService()
        result = svc.suggest_by_tags(db_session, create_location.id)
        assert len(result) == 1
        assert result[0].relation_type == "tags"

    def test_suggest_by_tags_no_overlap(self, db_session, create_location):
        no_tag_loc = Location(name="Different Tags", latitude=40.0, longitude=-3.0, tags=["indoor"], is_active=True)
        db_session.add(no_tag_loc)
        db_session.commit()
        svc = LocationRelationService()
        result = svc.suggest_by_tags(db_session, create_location.id)
        assert len(result) == 0

    def test_suggest_proximity_nonexistent_location(self, db_session):
        svc = LocationRelationService()
        assert svc.suggest_proximity(db_session, 999) == []

    def test_suggest_by_tags_nonexistent_location(self, db_session):
        svc = LocationRelationService()
        assert svc.suggest_by_tags(db_session, 999) == []
