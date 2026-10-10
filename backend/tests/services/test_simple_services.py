import pytest
from datetime import datetime, timezone

from app.models.user_session import UserSession

from app.schemas.festival import FestivalCreate
from app.schemas.shortfilm import ShortFilmCreate
from app.schemas.message import MessageCreate
from app.schemas.award import AwardCreate, AwardUpdate
from app.schemas.participant_tag import ParticipantTagCreate, FestivalParticipantTagCreate
from app.schemas.user_role import UserParticipantTagCreate
from app.schemas.user_alias import UserAliasCreate
from app.schemas.validation_rule import ValidationRuleCreate, ValidationRuleGroupCreate
from app.schemas.user_key import UserKeyUpload

from app.services.message_service import MessageService
from app.services.festival_service import FestivalService
from app.services.shortfilm_service import ShortFilmService
from app.services.award_service import AwardService
from app.services.participant_tag_service import (
    ParticipantTagService,
    FestivalParticipantTagService,
    UserParticipantTagService,
)  # noqa: E501
from app.services.user_alias_service import UserAliasService
from app.services.validation_rule_service import ValidationRuleService, ValidationRuleGroupService
from app.services.auth_session_service import AuthSessionService
from app.services.user_key_service import UserKeyService
from app.services.admin_service import AdminService
from app.services.user_festival_service import UserFestivalService


class TestMessageService:
    def setup_method(self):
        self.svc = MessageService()

    def test_create_message(self, db_session, create_user):
        user = create_user()
        msg_in = MessageCreate(content="Hello", sender_id=user.id, receiver_id=user.id)
        msg = self.svc.create(db_session, msg_in)
        assert msg.content == "Hello"
        assert msg.sender_id == user.id
        assert msg.is_read is False

    def test_get_multi_paginated_default(self, db_session, create_user):
        user = create_user()
        for i in range(5):
            self.svc.create(db_session, MessageCreate(content=f"Msg {i}", sender_id=user.id, receiver_id=user.id))
        result = self.svc.get_multi_paginated(db_session)
        assert result["total"] == 5
        assert len(result["items"]) == 5

    def test_get_multi_paginated_sender_filter(self, db_session, create_user):
        u1 = create_user("user1", "u1@test.com")
        u2 = create_user("user2", "u2@test.com")
        for i in range(3):
            self.svc.create(db_session, MessageCreate(content=f"A{i}", sender_id=u1.id, receiver_id=u2.id))
        for i in range(2):
            self.svc.create(db_session, MessageCreate(content=f"B{i}", sender_id=u2.id, receiver_id=u1.id))
        result = self.svc.get_multi_paginated(db_session, sender_id=u1.id)
        assert result["total"] == 3

    def test_get_multi_paginated_receiver_filter(self, db_session, create_user):
        u1 = create_user("user1", "u1@test.com")
        u2 = create_user("user2", "u2@test.com")
        self.svc.create(db_session, MessageCreate(content="Msg", sender_id=u1.id, receiver_id=u2.id))
        result = self.svc.get_multi_paginated(db_session, receiver_id=u2.id)
        assert result["total"] == 1

    def test_get_multi_paginated_group_filter(self, db_session, create_user):
        user = create_user()
        self.svc.create(db_session, MessageCreate(content="G1", sender_id=user.id, group_id=10))
        self.svc.create(db_session, MessageCreate(content="G2", sender_id=user.id, group_id=20))
        result = self.svc.get_multi_paginated(db_session, group_id=10)
        assert result["total"] == 1

    def test_get_multi_paginated_channel_filter(self, db_session, create_user):
        user = create_user()
        self.svc.create(db_session, MessageCreate(content="C1", sender_id=user.id, channel_id=5))
        self.svc.create(db_session, MessageCreate(content="C2", sender_id=user.id, channel_id=10))
        result = self.svc.get_multi_paginated(db_session, channel_id=5)
        assert result["total"] == 1

    def test_get_multi_paginated_unread_only(self, db_session, create_user):
        user = create_user()
        m1 = self.svc.create(db_session, MessageCreate(content="Unread", sender_id=user.id, receiver_id=user.id))
        self.svc.create(db_session, MessageCreate(content="Read", sender_id=user.id, receiver_id=user.id))
        m1.is_read = True
        db_session.commit()
        result = self.svc.get_multi_paginated(db_session, unread_only=True)
        assert result["total"] == 1

    def test_get_multi_paginated_pagination(self, db_session, create_user):
        user = create_user()
        for i in range(5):
            self.svc.create(db_session, MessageCreate(content=f"M{i}", sender_id=user.id, receiver_id=user.id))
        result = self.svc.get_multi_paginated(db_session, page=1, size=2)
        assert result["total"] == 5
        assert len(result["items"]) == 2
        assert result["page"] == 1
        assert result["size"] == 2
        assert result["pages"] == 3

    def test_mark_as_read(self, db_session, create_user):
        user = create_user()
        msg = self.svc.create(db_session, MessageCreate(content="Unread", sender_id=user.id, receiver_id=user.id))
        assert msg.is_read is False
        updated = self.svc.mark_as_read(db_session, msg.id)
        assert updated is not None
        assert updated.is_read is True

    def test_mark_as_read_not_found(self, db_session):
        result = self.svc.mark_as_read(db_session, 999)
        assert result is None

    def test_delete_message(self, db_session, create_user):
        user = create_user()
        msg = self.svc.create(db_session, MessageCreate(content="Del", sender_id=user.id, receiver_id=user.id))
        deleted = self.svc.delete(db_session, msg.id)
        assert deleted.id == msg.id
        assert self.svc.get(db_session, msg.id) is None

    def test_delete_not_found(self, db_session):
        assert self.svc.delete(db_session, 999) is None

    def test_get_not_found(self, db_session):
        assert self.svc.get(db_session, 999) is None

    def test_get_multi_empty(self, db_session):
        result = self.svc.get_multi_paginated(db_session)
        assert result["total"] == 0
        assert result["items"] == []


class TestFestivalService:
    def setup_method(self):
        self.svc = FestivalService()

    def test_create_festival(self, db_session):
        fest_in = FestivalCreate(name="Sunny Fest", location="Barcelona")
        fest = self.svc.create(db_session, fest_in)
        assert fest.name == "Sunny Fest"
        assert fest.location == "Barcelona"
        assert fest.is_active is True

    def test_get_multi_paginated_default(self, db_session):
        for i in range(3):
            self.svc.create(db_session, FestivalCreate(name=f"Fest {i}", location="City"))
        result = self.svc.get_multi_paginated(db_session)
        assert result["total"] == 3

    def test_get_multi_paginated_active_filter(self, db_session):
        f1 = self.svc.create(db_session, FestivalCreate(name="Active", location="A"))
        self.svc.create(db_session, FestivalCreate(name="Inactive", location="B"))
        f1.is_active = False
        db_session.commit()
        result = self.svc.get_multi_paginated(db_session, is_active=True)
        assert result["total"] == 1
        result2 = self.svc.get_multi_paginated(db_session, is_active=False)
        assert result2["total"] == 1

    def test_get_multi_paginated_pagination(self, db_session):
        for i in range(10):
            self.svc.create(db_session, FestivalCreate(name=f"F{i}", location="L"))
        result = self.svc.get_multi_paginated(db_session, page=1, size=3)
        assert len(result["items"]) == 3
        assert result["pages"] == 4

    def test_get_festival(self, db_session):
        fest = self.svc.create(db_session, FestivalCreate(name="Unique", location="Loc"))
        found = self.svc.get(db_session, fest.id)
        assert found is not None
        assert found.name == "Unique"

    def test_update_festival(self, db_session):
        fest = self.svc.create(db_session, FestivalCreate(name="Old", location="Loc"))
        from app.schemas.festival import FestivalUpdate

        updated = self.svc.update(db_session, fest.id, FestivalUpdate(name="New"))
        assert updated.name == "New"

    def test_delete_festival(self, db_session):
        fest = self.svc.create(db_session, FestivalCreate(name="Del", location="L"))
        self.svc.delete(db_session, fest.id)
        assert self.svc.get(db_session, fest.id) is None


class TestShortFilmService:
    def setup_method(self):
        self.svc = ShortFilmService()

    def test_create_shortfilm(self, db_session, create_user):
        user = create_user()
        sf = self.svc.create(db_session, ShortFilmCreate(title="My Film", user_id=user.id))
        assert sf.title == "My Film"
        assert sf.user_id == user.id
        assert sf.is_public is True

    def test_get_multi_paginated_default(self, db_session, create_user):
        user = create_user()
        for i in range(4):
            self.svc.create(db_session, ShortFilmCreate(title=f"F{i}", user_id=user.id))
        result = self.svc.get_multi_paginated(db_session)
        assert result["total"] == 4

    def test_get_multi_paginated_festival_filter(self, db_session, create_user, create_festival):
        user = create_user()
        f1 = create_festival("F1")
        f2 = create_festival("F2")
        self.svc.create(db_session, ShortFilmCreate(title="A", user_id=user.id, festival_id=f1.id))
        self.svc.create(db_session, ShortFilmCreate(title="B", user_id=user.id, festival_id=f2.id))
        result = self.svc.get_multi_paginated(db_session, festival_id=f1.id)
        assert result["total"] == 1

    def test_get_multi_paginated_user_filter(self, db_session, create_user):
        u1 = create_user("u1", "u1@t.com")
        u2 = create_user("u2", "u2@t.com")
        self.svc.create(db_session, ShortFilmCreate(title="U1Film", user_id=u1.id))
        self.svc.create(db_session, ShortFilmCreate(title="U2Film", user_id=u2.id))
        result = self.svc.get_multi_paginated(db_session, user_id=u1.id)
        assert result["total"] == 1

    def test_get_multi_paginated_public_filter(self, db_session, create_user):
        user = create_user()
        sf = self.svc.create(db_session, ShortFilmCreate(title="Private", user_id=user.id))
        sf.is_public = False
        db_session.commit()
        self.svc.create(db_session, ShortFilmCreate(title="Public", user_id=user.id))
        result = self.svc.get_multi_paginated(db_session, is_public=True)
        assert result["total"] == 1
        result2 = self.svc.get_multi_paginated(db_session, is_public=False)
        assert result2["total"] == 1


class TestAwardService:
    def setup_method(self):
        self.svc = AwardService()

    def test_create(self, db_session, create_festival, create_user):
        fest = create_festival()
        create_user()
        award_in = AwardCreate(festival_id=fest.id, award_name="Best Film")
        award = self.svc.create(db_session, award_in)
        assert award.award_name == "Best Film"
        assert award.festival_id == fest.id
        assert award.is_verified is False

    def test_create_with_extra_fields(self, db_session, create_festival, create_user):
        fest = create_festival()
        user = create_user()
        award_in = AwardCreate(festival_id=fest.id, award_name="Best Director")
        award = self.svc.create(db_session, award_in, user_id=user.id, created_by=user.id)
        assert award.user_id == user.id
        assert award.created_by == user.id

    def test_get_by_festival(self, db_session, create_festival, create_user):
        f1 = create_festival("F1")
        f2 = create_festival("F2")
        create_user()
        for i in range(3):
            self.svc.create(db_session, AwardCreate(festival_id=f1.id, award_name=f"A{i}"))
        self.svc.create(db_session, AwardCreate(festival_id=f2.id, award_name="Other"))
        result = self.svc.get_by_festival(db_session, f1.id)
        assert len(result) == 3

    def test_get_by_festival_user_filter(self, db_session, create_festival, create_user):
        fest = create_festival()
        u1 = create_user("u1", "u1@t.com")
        u2 = create_user("u2", "u2@t.com")
        self.svc.create(db_session, AwardCreate(festival_id=fest.id, award_name="Best"), user_id=u1.id)
        self.svc.create(db_session, AwardCreate(festival_id=fest.id, award_name="Best2"), user_id=u2.id)
        result = self.svc.get_by_festival(db_session, fest.id, user_id=u1.id)
        assert len(result) == 1

    def test_get_by_festival_is_public_filter(self, db_session, create_festival, create_user):
        fest = create_festival()
        create_user()
        self.svc.create(db_session, AwardCreate(festival_id=fest.id, award_name="Public", is_public=True))
        self.svc.create(db_session, AwardCreate(festival_id=fest.id, award_name="Private", is_public=False))
        result = self.svc.get_by_festival(db_session, fest.id, is_public=True)
        assert len(result) == 1
        result2 = self.svc.get_by_festival(db_session, fest.id, is_public=False)
        assert len(result2) == 1

    def test_get_by_user(self, db_session, create_festival, create_user):
        fest = create_festival()
        u1 = create_user("u1", "u1@t.com")
        u2 = create_user("u2", "u2@t.com")
        self.svc.create(db_session, AwardCreate(festival_id=fest.id, award_name="A1"), user_id=u1.id)
        self.svc.create(db_session, AwardCreate(festival_id=fest.id, award_name="A2"), user_id=u1.id)
        self.svc.create(db_session, AwardCreate(festival_id=fest.id, award_name="B1"), user_id=u2.id)
        result = self.svc.get_by_user(db_session, u1.id)
        assert len(result) == 2

    def test_get_by_user_is_public_filter(self, db_session, create_festival, create_user):
        fest = create_festival()
        user = create_user()
        self.svc.create(db_session, AwardCreate(festival_id=fest.id, award_name="Pub", is_public=True), user_id=user.id)
        self.svc.create(
            db_session, AwardCreate(festival_id=fest.id, award_name="Priv", is_public=False), user_id=user.id
        )  # noqa: E501
        result = self.svc.get_by_user(db_session, user.id, is_public=True)
        assert len(result) == 1

    def test_update_with_verification(self, db_session, create_festival, create_user):
        fest = create_festival()
        create_user()
        verifier = create_user("verifier", "v@t.com")
        award = self.svc.create(db_session, AwardCreate(festival_id=fest.id, award_name="Best"))
        assert award.is_verified is False
        updated = self.svc.update_with_verification(db_session, award.id, AwardUpdate(award_name="Winner"), verifier.id)
        assert updated.award_name == "Winner"
        assert updated.is_verified is True
        assert updated.verified_by == verifier.id

    def test_update_with_verification_not_found(self, db_session, create_user):
        verifier = create_user()
        result = self.svc.update_with_verification(db_session, 999, AwardUpdate(award_name="X"), verifier.id)
        assert result is None

    def test_update_with_verification_explicit_false(self, db_session, create_festival, create_user):
        fest = create_festival()
        user = create_user()
        award = self.svc.create(db_session, AwardCreate(festival_id=fest.id, award_name="Test"))
        updated = self.svc.update_with_verification(db_session, award.id, AwardUpdate(is_verified=False), user.id)
        assert updated.is_verified is False
        assert updated.verified_by == user.id


class TestParticipantTagService:
    def setup_method(self):
        self.svc = ParticipantTagService()
        self.fest_tag_svc = FestivalParticipantTagService()
        self.user_tag_svc = UserParticipantTagService()

    def test_create_tag(self, db_session):
        tag_in = ParticipantTagCreate(name="director", display_name="Director", category="direction")
        tag = self.svc.create(db_session, tag_in)
        assert tag.name == "director"
        assert tag.category == "direction"

    def test_get_all_tags(self, db_session):
        self.svc.create(db_session, ParticipantTagCreate(name="a", display_name="A", category="acting"))
        self.svc.create(db_session, ParticipantTagCreate(name="b", display_name="B", category="sound"))
        result = self.svc.get_all(db_session)
        assert len(result) == 2

    def test_get_all_by_category(self, db_session):
        self.svc.create(db_session, ParticipantTagCreate(name="actor", display_name="Actor", category="acting"))
        self.svc.create(db_session, ParticipantTagCreate(name="sounder", display_name="Sounder", category="sound"))
        result = self.svc.get_all(db_session, category="acting")
        assert len(result) == 1
        assert result[0].name == "actor"

    def test_get_by_name(self, db_session):
        self.svc.create(db_session, ParticipantTagCreate(name="editor", display_name="Editor", category="editing"))
        tag = self.svc.get_by_name(db_session, "editor")
        assert tag is not None
        assert tag.display_name == "Editor"

    def test_get_by_name_not_found(self, db_session):
        assert self.svc.get_by_name(db_session, "nonexistent") is None

    def test_get_all_empty(self, db_session):
        assert self.svc.get_all(db_session) == []

    def test_festival_participant_tag_create(self, db_session, create_festival):
        fest = create_festival()
        tag = self.svc.create(db_session, ParticipantTagCreate(name="tag1", display_name="Tag1", category="other"))
        ftag_in = FestivalParticipantTagCreate(festival_id=fest.id, tag_id=tag.id, is_required=True)
        ftag = self.fest_tag_svc.create(db_session, ftag_in)
        assert ftag.festival_id == fest.id
        assert ftag.tag_id == tag.id
        assert ftag.is_required is True

    def test_festival_participant_tag_get_by_festival(self, db_session, create_festival):
        fest = create_festival()
        t1 = self.svc.create(db_session, ParticipantTagCreate(name="x", display_name="X", category="other"))
        t2 = self.svc.create(db_session, ParticipantTagCreate(name="y", display_name="Y", category="other"))
        self.fest_tag_svc.create(db_session, FestivalParticipantTagCreate(festival_id=fest.id, tag_id=t1.id))
        self.fest_tag_svc.create(db_session, FestivalParticipantTagCreate(festival_id=fest.id, tag_id=t2.id))
        result = self.fest_tag_svc.get_by_festival(db_session, fest.id)
        assert len(result) == 2

    def test_festival_participant_tag_get_by_festival_and_tag(self, db_session, create_festival):
        fest = create_festival()
        tag = self.svc.create(db_session, ParticipantTagCreate(name="z", display_name="Z", category="other"))
        ftag = self.fest_tag_svc.create(db_session, FestivalParticipantTagCreate(festival_id=fest.id, tag_id=tag.id))
        found = self.fest_tag_svc.get_by_festival_and_tag(db_session, fest.id, tag.id)
        assert found is not None
        assert found.id == ftag.id

    def test_festival_participant_tag_empty(self, db_session):
        assert self.fest_tag_svc.get_by_festival(db_session, 999) == []

    def test_user_participant_tag_create(self, db_session, create_user):
        user = create_user()
        tag = self.svc.create(db_session, ParticipantTagCreate(name="actor", display_name="Actor", category="acting"))
        utag_in = UserParticipantTagCreate(user_id=user.id, tag_id=tag.id, is_primary=True)
        utag = self.user_tag_svc.create(db_session, utag_in)
        assert utag.user_id == user.id
        assert utag.tag_id == tag.id
        assert utag.is_primary is True

    def test_user_participant_tag_get_by_user(self, db_session, create_user):
        user = create_user()
        t1 = self.svc.create(db_session, ParticipantTagCreate(name="d", display_name="D", category="direction"))
        t2 = self.svc.create(db_session, ParticipantTagCreate(name="e", display_name="E", category="editing"))
        self.user_tag_svc.create(db_session, UserParticipantTagCreate(user_id=user.id, tag_id=t1.id))
        self.user_tag_svc.create(db_session, UserParticipantTagCreate(user_id=user.id, tag_id=t2.id))
        result = self.user_tag_svc.get_by_user(db_session, user.id)
        assert len(result) == 2

    def test_user_participant_tag_get_by_user_and_tag(self, db_session, create_user):
        user = create_user()
        tag = self.svc.create(db_session, ParticipantTagCreate(name="cam", display_name="Camera", category="camera"))
        self.user_tag_svc.create(db_session, UserParticipantTagCreate(user_id=user.id, tag_id=tag.id))
        found = self.user_tag_svc.get_by_user_and_tag(db_session, user.id, tag.id)
        assert found is not None


class TestUserAliasService:
    def setup_method(self):
        self.svc = UserAliasService()

    def test_create_alias(self, db_session, create_user):
        user = create_user()
        alias_in = UserAliasCreate(user_id=user.id, alias="Nick", context="global")
        alias = self.svc.create(db_session, alias_in)
        assert alias.user_id == user.id
        assert alias.alias == "Nick"

    def test_get_by_user(self, db_session, create_user):
        user = create_user()
        self.svc.create(db_session, UserAliasCreate(user_id=user.id, alias="A", context="global"))
        self.svc.create(db_session, UserAliasCreate(user_id=user.id, alias="B", context="festival", context_id=1))
        result = self.svc.get_by_user(db_session, user.id)
        assert len(result) == 2

    def test_get_by_user_context_filter(self, db_session, create_user):
        user = create_user()
        self.svc.create(db_session, UserAliasCreate(user_id=user.id, alias="Global", context="global"))
        self.svc.create(db_session, UserAliasCreate(user_id=user.id, alias="Fest", context="festival", context_id=5))
        result = self.svc.get_by_user(db_session, user.id, context="festival")
        assert len(result) == 1
        assert result[0].alias == "Fest"

    def test_get_by_token(self, db_session, create_user):
        user = create_user()
        alias = self.svc.create(
            db_session, UserAliasCreate(user_id=user.id, alias="Public", context="global", profile_token="abc123")
        )  # noqa: E501
        found = self.svc.get_by_token(db_session, "abc123")
        assert found is not None
        assert found.id == alias.id

    def test_get_by_token_private(self, db_session, create_user):
        user = create_user()
        self.svc.create(
            db_session,
            UserAliasCreate(user_id=user.id, alias="Priv", context="global", profile_token="secret", is_public=False),
        )  # noqa: E501
        found = self.svc.get_by_token(db_session, "secret")
        assert found is None

    def test_get_by_token_not_found(self, db_session):
        assert self.svc.get_by_token(db_session, "nonexistent") is None

    def test_get_by_user_and_context(self, db_session, create_user):
        user = create_user()
        self.svc.create(
            db_session, UserAliasCreate(user_id=user.id, alias="FestAlias", context="festival", context_id=10)
        )  # noqa: E501
        found = self.svc.get_by_user_and_context(db_session, user.id, "festival", 10)
        assert found is not None
        assert found.alias == "FestAlias"

    def test_get_by_user_and_context_not_found(self, db_session, create_user):
        user = create_user()
        assert self.svc.get_by_user_and_context(db_session, user.id, "festival", 999) is None


class TestValidationRuleService:
    def setup_method(self):
        self.svc = ValidationRuleService()
        self.group_svc = ValidationRuleGroupService()

    def test_create_rule(self, db_session):
        rule_in = ValidationRuleCreate(name="Full Name", field_name="full_name", field_label="Full Name")
        rule = self.svc.create(db_session, rule_in)
        assert rule.name == "Full Name"
        assert rule.field_name == "full_name"

    def test_get_all_rules(self, db_session):
        self.svc.create(db_session, ValidationRuleCreate(name="R1", field_name="f1", field_label="F1"))
        self.svc.create(db_session, ValidationRuleCreate(name="R2", field_name="f2", field_label="F2"))
        result = self.svc.get_all(db_session)
        assert len(result) == 2

    def test_get_all_by_scope(self, db_session):
        self.svc.create(
            db_session, ValidationRuleCreate(name="Global", field_name="g", field_label="G", scope="global")
        )  # noqa: E501
        self.svc.create(
            db_session, ValidationRuleCreate(name="Fest", field_name="f", field_label="F", scope="festival", scope_id=1)
        )  # noqa: E501
        result = self.svc.get_all(db_session, scope="festival")
        assert len(result) == 1

    def test_get_all_by_scope_id(self, db_session):
        self.svc.create(
            db_session, ValidationRuleCreate(name="F1", field_name="a", field_label="A", scope="festival", scope_id=1)
        )  # noqa: E501
        self.svc.create(
            db_session, ValidationRuleCreate(name="F2", field_name="b", field_label="B", scope="festival", scope_id=2)
        )  # noqa: E501
        result = self.svc.get_all(db_session, scope="festival", scope_id=1)
        assert len(result) == 1

    def test_get_all_empty(self, db_session):
        assert self.svc.get_all(db_session) == []

    def test_create_group(self, db_session):
        group_in = ValidationRuleGroupCreate(name="Profile Rules", scope="global")
        group = self.group_svc.create_with_rules(db_session, group_in)
        assert group.name == "Profile Rules"
        assert group.is_active is True

    def test_create_group_via_base_fails(self, db_session):
        from pydantic import BaseModel

        class _GroupCreate(BaseModel):
            name: str
            scope: str = "global"
            description: str | None = None
            is_active: bool = True
            scope_id: int | None = None

        group_in = _GroupCreate(name="Direct", scope="global")
        group = self.group_svc.create(db_session, group_in)
        assert group.name == "Direct"

    def test_get_all_groups(self, db_session):
        self.group_svc.create_with_rules(db_session, ValidationRuleGroupCreate(name="G1", scope="global"))
        self.group_svc.create_with_rules(db_session, ValidationRuleGroupCreate(name="G2", scope="festival"))
        result = self.group_svc.get_all(db_session)
        assert len(result) == 2

    def test_get_all_groups_by_scope(self, db_session):
        self.group_svc.create_with_rules(db_session, ValidationRuleGroupCreate(name="A", scope="global"))
        self.group_svc.create_with_rules(db_session, ValidationRuleGroupCreate(name="B", scope="festival"))
        result = self.group_svc.get_all(db_session, scope="festival")
        assert len(result) == 1

    def test_create_group_with_rules(self, db_session):
        r1 = self.svc.create(db_session, ValidationRuleCreate(name="N", field_name="name", field_label="Name"))
        r2 = self.svc.create(db_session, ValidationRuleCreate(name="E", field_name="email", field_label="Email"))
        group_in = ValidationRuleGroupCreate(name="With Rules", scope="global", rule_ids=[r1.id, r2.id])
        group = self.group_svc.create_with_rules(db_session, group_in)
        assert group.name == "With Rules"
        from app.models.validation_rule import validation_rule_group_rules

        rows = db_session.execute(
            validation_rule_group_rules.select().where(validation_rule_group_rules.c.group_id == group.id)
        ).fetchall()
        assert len(rows) == 2

    def test_create_group_without_rules(self, db_session):
        group_in = ValidationRuleGroupCreate(name="Empty Group", scope="global")
        group = self.group_svc.create_with_rules(db_session, group_in)
        assert group.name == "Empty Group"


class TestAuthSessionService:
    def setup_method(self):
        self.svc = AuthSessionService()

    def _make_session(self, db, user_id, is_active=True, **kw):
        from datetime import datetime, timedelta, timezone

        obj = UserSession(
            user_id=user_id,
            token_hash=kw.get("token_hash", "tok_" + str(user_id)),
            refresh_token_hash=kw.get("refresh_hash", "ref_" + str(user_id)),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            is_active=is_active,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def test_create(self, db_session, create_user):
        from datetime import datetime, timedelta, timezone

        user = create_user()
        sess = UserSession(
            user_id=user.id,
            token_hash="tok_create",
            refresh_token_hash="ref_create",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db_session.add(sess)
        db_session.commit()
        db_session.refresh(sess)
        assert sess.user_id == user.id
        assert sess.is_active is True

    def test_get_by_user(self, db_session, create_user):
        user = create_user()
        self._make_session(db_session, user.id)
        self._make_session(db_session, user.id, token_hash="tok2", refresh_hash="ref2")
        sessions = self.svc.get_by_user(db_session, user.id)
        assert len(sessions) == 2

    def test_get_by_user_empty(self, db_session, create_user):
        user = create_user()
        assert self.svc.get_by_user(db_session, user.id) == []

    def test_get_by_refresh_token_hash(self, db_session, create_user):
        user = create_user()
        sess = self._make_session(db_session, user.id, refresh_hash="my_refresh_hash")
        found = self.svc.get_by_refresh_token_hash(db_session, "my_refresh_hash")
        assert found is not None
        assert found.id == sess.id

    def test_get_by_refresh_token_hash_revoked(self, db_session, create_user):
        user = create_user()
        sess = self._make_session(db_session, user.id, refresh_hash="revoked_hash")
        sess.revoked_at = datetime.now(timezone.utc)
        sess.is_active = False
        db_session.commit()
        found = self.svc.get_by_refresh_token_hash(db_session, "revoked_hash")
        assert found is None

    def test_get_by_refresh_token_hash_not_found(self, db_session):
        assert self.svc.get_by_refresh_token_hash(db_session, "nonexistent") is None

    def test_get_user_sessions_paginated(self, db_session, create_user):
        user = create_user()
        for i in range(5):
            self._make_session(db_session, user.id, token_hash=f"t{i}", refresh_hash=f"r{i}")
        result = self.svc.get_user_sessions_paginated(db_session, user.id, page=1, size=2)
        assert result["total"] == 5
        assert len(result["items"]) == 2

    def test_revoke_session(self, db_session, create_user):
        user = create_user()
        sess = self._make_session(db_session, user.id)
        assert sess.is_active is True
        assert sess.revoked_at is None
        revoked = self.svc.revoke_session(db_session, sess.id)
        assert revoked.is_active is False
        assert revoked.revoked_at is not None

    def test_revoke_session_not_found(self, db_session):
        result = self.svc.revoke_session(db_session, 999)
        assert result is None

    def test_revoke_all_user_sessions(self, db_session, create_user):
        user = create_user()
        self._make_session(db_session, user.id, token_hash="t1", refresh_hash="r1")
        self._make_session(db_session, user.id, token_hash="t2", refresh_hash="r2")
        count = self.svc.revoke_all_user_sessions(db_session, user.id)
        assert count == 2
        sessions = self.svc.get_by_user(db_session, user.id)
        for s in sessions:
            assert s.is_active is False

    def test_revoke_all_user_sessions_only_active(self, db_session, create_user):
        user = create_user()
        self._make_session(db_session, user.id, token_hash="t1", refresh_hash="r1")
        self._make_session(db_session, user.id, token_hash="t2", refresh_hash="r2", is_active=False)
        count = self.svc.revoke_all_user_sessions(db_session, user.id)
        assert count == 1


class TestUserKeyService:
    def setup_method(self):
        self.svc = UserKeyService()

    def test_set_or_update_public_key_create(self, db_session, create_user):
        user = create_user()
        key_data = UserKeyUpload(public_key_x25519="base64encodedkey123")
        key = self.svc.set_or_update_public_key(db_session, user.id, key_data)
        assert key.user_id == user.id
        assert key.public_key_x25519 == "base64encodedkey123"
        assert len(key.key_identifier) == 16

    def test_set_or_update_public_key_update(self, db_session, create_user):
        user = create_user()
        key_data = UserKeyUpload(public_key_x25519="firstkeyvalue")
        key = self.svc.set_or_update_public_key(db_session, user.id, key_data)
        old_fingerprint = key.key_identifier
        new_key_data = UserKeyUpload(public_key_x25519="updatedkeyvalue")
        updated = self.svc.set_or_update_public_key(db_session, user.id, new_key_data)
        assert updated.public_key_x25519 == "updatedkeyvalue"
        assert updated.key_identifier != old_fingerprint
        assert updated.is_active == 1
        assert updated.rotated_at is not None

    def test_set_or_update_public_key_fingerprint(self, db_session, create_user):
        import hashlib

        user = create_user()
        key_data = UserKeyUpload(public_key_x25519="testkeydata")
        key = self.svc.set_or_update_public_key(db_session, user.id, key_data)
        expected_fp = hashlib.sha256(b"testkeydata").hexdigest()[:16]
        assert key.key_identifier == expected_fp

    def test_get_by_user(self, db_session, create_user):
        user = create_user()
        key_data = UserKeyUpload(public_key_x25519="somekey")
        self.svc.set_or_update_public_key(db_session, user.id, key_data)
        found = self.svc.get_by_user(db_session, user.id)
        assert found is not None
        assert found.public_key_x25519 == "somekey"

    def test_get_by_user_no_key(self, db_session, create_user):
        user = create_user()
        assert self.svc.get_by_user(db_session, user.id) is None

    def test_get_by_user_inactive(self, db_session, create_user):
        user = create_user()
        key_data = UserKeyUpload(public_key_x25519="key")
        key = self.svc.set_or_update_public_key(db_session, user.id, key_data)
        key.is_active = 0
        db_session.commit()
        assert self.svc.get_by_user(db_session, user.id) is None


class TestAdminService:
    def setup_method(self):
        self.svc = AdminService()

    def test_get_stats_empty(self, db_session):
        stats = self.svc.get_stats(db_session)
        assert stats["users"] == 0
        assert stats["festivals"] == 0
        assert stats["shortfilms"] == 0
        assert stats["messages"] == 0
        assert stats["active_users"] == 0
        assert stats["active_festivals"] == 0

    def test_get_stats_with_data(self, db_session, create_user, create_festival, create_shortfilm):
        u1 = create_user("u1", "u1@t.com")
        create_user("u2", "u2@t.com")
        u3 = create_user("u3", "u3@t.com")
        u3.is_active = False
        db_session.commit()
        f1 = create_festival("Active Fest")
        f2 = create_festival("Inactive Fest")
        f2.is_active = False
        db_session.commit()
        create_shortfilm(title="Film1", user_id=u1.id, festival_id=f1.id)
        stats = self.svc.get_stats(db_session)
        assert stats["users"] == 3
        assert stats["active_users"] == 2
        assert stats["festivals"] == 2
        assert stats["active_festivals"] == 1
        assert stats["shortfilms"] == 1
        assert stats["messages"] == 0

    def test_get_tables(self, db_session):
        tables = self.svc.get_tables(db_session)
        assert "tables" in tables
        assert isinstance(tables["tables"], dict)
        assert "users" in tables["tables"]
        assert "festivals" in tables["tables"]
        assert "shortfilms" in tables["tables"]
        assert "messages" in tables["tables"]
        assert "alembic_version" not in tables["tables"]


class TestUserFestivalService:
    def setup_method(self):
        self.svc = UserFestivalService()

    def test_join_festival(self, db_session, create_user, create_festival):
        user = create_user()
        fest = create_festival()
        self.svc.join_festival(db_session, user.id, fest.id)
        assert self.svc.is_member(db_session, user.id, fest.id) is True

    def test_join_festival_with_role(self, db_session, create_user, create_festival):
        user = create_user()
        fest = create_festival()
        self.svc.join_festival(db_session, user.id, fest.id, role="organizer")
        assert self.svc.is_member(db_session, user.id, fest.id) is True

    def test_leave_festival(self, db_session, create_user, create_festival):
        user = create_user()
        fest = create_festival()
        self.svc.join_festival(db_session, user.id, fest.id)
        result = self.svc.leave_festival(db_session, user.id, fest.id)
        assert result is True
        assert self.svc.is_member(db_session, user.id, fest.id) is False

    def test_leave_festival_not_member(self, db_session, create_user, create_festival):
        user = create_user()
        fest = create_festival()
        result = self.svc.leave_festival(db_session, user.id, fest.id)
        assert result is False

    def test_is_member_true(self, db_session, create_user, create_festival):
        user = create_user()
        fest = create_festival()
        self.svc.join_festival(db_session, user.id, fest.id)
        assert self.svc.is_member(db_session, user.id, fest.id) is True

    def test_is_member_false(self, db_session, create_user, create_festival):
        user = create_user()
        fest = create_festival()
        assert self.svc.is_member(db_session, user.id, fest.id) is False

    def test_get_festival_members(self, db_session, create_user, create_festival):
        u1 = create_user("u1", "u1@t.com")
        u2 = create_user("u2", "u2@t.com")
        fest = create_festival()
        self.svc.join_festival(db_session, u1.id, fest.id, role="jury")
        self.svc.join_festival(db_session, u2.id, fest.id, role="organizer")
        members = self.svc.get_festival_members(db_session, fest.id)
        assert len(members) == 2
        usernames = [m["username"] for m in members]
        assert "u1" in usernames
        assert "u2" in usernames

    def test_get_festival_members_empty(self, db_session, create_festival):
        fest = create_festival()
        assert self.svc.get_festival_members(db_session, fest.id) == []

    def test_get_user_festivals(self, db_session, create_user, create_festival):
        user = create_user()
        f1 = create_festival("Fest A")
        f2 = create_festival("Fest B")
        self.svc.join_festival(db_session, user.id, f1.id, role="jury")
        self.svc.join_festival(db_session, user.id, f2.id)
        festivals = self.svc.get_user_festivals(db_session, user.id)
        assert len(festivals) == 2
        names = [f["name"] for f in festivals]
        assert "Fest A" in names
        assert "Fest B" in names

    def test_get_user_festivals_empty(self, db_session, create_user):
        user = create_user()
        assert self.svc.get_user_festivals(db_session, user.id) == []

    def test_join_twice_raises(self, db_session, create_user, create_festival):
        import sqlalchemy

        user = create_user()
        fest = create_festival()
        self.svc.join_festival(db_session, user.id, fest.id)
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            self.svc.join_festival(db_session, user.id, fest.id)
