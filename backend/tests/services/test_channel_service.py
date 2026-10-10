import pytest
from fastapi import HTTPException
from app.schemas.channel import ChannelCreate
from app.models.channel import ChannelMember
from app.services.channel_service import ChannelService

svc = ChannelService()


def test_create_channel_adds_creator_as_admin(db_session, create_user):
    user = create_user()
    obj_in = ChannelCreate(name="General", channel_type="community")
    channel = svc.create_channel(db_session, obj_in, created_by=user.id)
    assert channel.name == "General"
    assert channel.channel_type == "community"
    assert channel.created_by == user.id
    assert channel.is_active is True
    member = (
        db_session.query(ChannelMember)
        .filter(
            ChannelMember.channel_id == channel.id,
            ChannelMember.user_id == user.id,
        )
        .first()
    )
    assert member is not None
    assert member.role == "admin"
    assert member.is_active is True


def test_create_private_channel_default_max_members(db_session, create_user):
    user = create_user()
    obj_in = ChannelCreate(name="Private Chat", channel_type="private")
    channel = svc.create_channel(db_session, obj_in, created_by=user.id)
    assert channel.channel_type == "private"
    assert channel.max_members == 20


def test_get_channels_for_user_returns_member_channels(db_session, create_user):
    user1 = create_user("alice", email="alice@example.com")
    user2 = create_user("bob", email="bob@example.com")
    obj_in = ChannelCreate(name="Team", channel_type="community")
    channel = svc.create_channel(db_session, obj_in, created_by=user1.id)
    svc.add_member(db_session, channel.id, user2.id)
    result = svc.get_channels_for_user(db_session, user2.id)
    assert len(result["items"]) == 1
    assert result["items"][0].id == channel.id


def test_get_channels_for_user_empty_for_non_member(db_session, create_user):
    user1 = create_user("alice", email="alice@example.com")
    user2 = create_user("bob", email="bob@example.com")
    obj_in = ChannelCreate(name="Team", channel_type="community")
    svc.create_channel(db_session, obj_in, created_by=user1.id)
    result = svc.get_channels_for_user(db_session, user2.id)
    assert len(result["items"]) == 0


def test_get_public_channels_returns_community_channels(db_session, create_user):
    user = create_user()
    obj_in = ChannelCreate(name="Public", channel_type="community")
    svc.create_channel(db_session, obj_in, created_by=user.id)
    obj_in2 = ChannelCreate(name="Private", channel_type="private")
    svc.create_channel(db_session, obj_in2, created_by=user.id)
    result = svc.get_public_channels(db_session)
    assert len(result["items"]) == 1
    assert result["items"][0].name == "Public"


def test_get_public_channels_excludes_non_community(db_session, create_user):
    user = create_user()
    obj_in = ChannelCreate(name="Private", channel_type="private")
    svc.create_channel(db_session, obj_in, created_by=user.id)
    result = svc.get_public_channels(db_session)
    assert len(result["items"]) == 0


def test_get_member_count(db_session, create_user):
    user1 = create_user("alice", email="alice@example.com")
    user2 = create_user("bob", email="bob@example.com")
    obj_in = ChannelCreate(name="Team", channel_type="community")
    channel = svc.create_channel(db_session, obj_in, created_by=user1.id)
    svc.add_member(db_session, channel.id, user2.id)
    count = svc.get_member_count(db_session, channel.id)
    assert count == 2


def test_add_member_creates_new_member(db_session, create_user):
    owner = create_user("owner", email="owner@example.com")
    member = create_user("member", email="member@example.com")
    obj_in = ChannelCreate(name="Team", channel_type="community")
    channel = svc.create_channel(db_session, obj_in, created_by=owner.id)
    m = svc.add_member(db_session, channel.id, member.id)
    assert m.channel_id == channel.id
    assert m.user_id == member.id
    assert m.role == "member"
    assert m.is_active is True


def test_add_member_raises_400_if_already_member(db_session, create_user):
    owner = create_user("owner", email="owner@example.com")
    member = create_user("member", email="member@example.com")
    obj_in = ChannelCreate(name="Team", channel_type="community")
    channel = svc.create_channel(db_session, obj_in, created_by=owner.id)
    svc.add_member(db_session, channel.id, member.id)
    with pytest.raises(HTTPException) as exc:
        svc.add_member(db_session, channel.id, member.id)
    assert exc.value.status_code == 400


def test_add_member_raises_400_if_channel_full(db_session, create_user):
    owner = create_user("owner", email="owner@example.com")
    extra = create_user("extra", email="extra@example.com")
    obj_in = ChannelCreate(name="Tiny", channel_type="private", max_members=1)
    channel = svc.create_channel(db_session, obj_in, created_by=owner.id)
    with pytest.raises(HTTPException) as exc:
        svc.add_member(db_session, channel.id, extra.id)
    assert exc.value.status_code == 400
    assert "full" in str(exc.value.detail).lower()


def test_add_member_raises_404_if_channel_not_found(db_session, create_user):
    user = create_user()
    with pytest.raises(HTTPException) as exc:
        svc.add_member(db_session, 999, user.id)
    assert exc.value.status_code == 404


def test_add_member_reactivates_inactive_membership(db_session, create_user):
    owner = create_user("owner", email="owner@example.com")
    member = create_user("member", email="member@example.com")
    obj_in = ChannelCreate(name="Team", channel_type="community")
    channel = svc.create_channel(db_session, obj_in, created_by=owner.id)
    added = svc.add_member(db_session, channel.id, member.id)
    svc.remove_member(db_session, channel.id, member.id)
    reactivated = svc.add_member(db_session, channel.id, member.id)
    assert reactivated.id == added.id
    assert reactivated.is_active is True
    assert reactivated.role == "member"


def test_remove_member_deactivates_membership(db_session, create_user):
    owner = create_user("owner")
    obj_in = ChannelCreate(name="Team", channel_type="community")
    channel = svc.create_channel(db_session, obj_in, created_by=owner.id)
    svc.remove_member(db_session, channel.id, owner.id)
    member = (
        db_session.query(ChannelMember)
        .filter(
            ChannelMember.channel_id == channel.id,
            ChannelMember.user_id == owner.id,
        )
        .first()
    )
    assert member.is_active is False


def test_remove_member_raises_404_if_not_member(db_session, create_user):
    owner = create_user("owner")
    obj_in = ChannelCreate(name="Team", channel_type="community")
    channel = svc.create_channel(db_session, obj_in, created_by=owner.id)
    with pytest.raises(HTTPException) as exc:
        svc.remove_member(db_session, channel.id, 999)
    assert exc.value.status_code == 404


def test_get_members_returns_active_members(db_session, create_user):
    user1 = create_user("alice", email="alice@example.com")
    user2 = create_user("bob", email="bob@example.com")
    obj_in = ChannelCreate(name="Team", channel_type="community")
    channel = svc.create_channel(db_session, obj_in, created_by=user1.id)
    svc.add_member(db_session, channel.id, user2.id)
    members = svc.get_members(db_session, channel.id)
    assert len(members) == 2
    assert all(m.is_active is True for m in members)


def test_soft_delete_deactivates_channel(db_session, create_user):
    user = create_user()
    obj_in = ChannelCreate(name="Temp", channel_type="community")
    channel = svc.create_channel(db_session, obj_in, created_by=user.id)
    result = svc.soft_delete(db_session, channel.id)
    assert result is not None
    assert result.is_active is False


def test_soft_delete_returns_none_for_non_existent(db_session):
    result = svc.soft_delete(db_session, 999)
    assert result is None


def test_get_member_role_returns_role(db_session, create_user):
    user = create_user()
    obj_in = ChannelCreate(name="Team", channel_type="community")
    channel = svc.create_channel(db_session, obj_in, created_by=user.id)
    role = svc.get_member_role(db_session, channel.id, user.id)
    assert role == "admin"


def test_get_member_role_returns_none_if_not_member(db_session, create_user):
    user = create_user()
    obj_in = ChannelCreate(name="Team", channel_type="community")
    channel = svc.create_channel(db_session, obj_in, created_by=user.id)
    role = svc.get_member_role(db_session, channel.id, 999)
    assert role is None


def test_update_member_role_updates_role(db_session, create_user):
    owner = create_user("owner", email="owner@example.com")
    member = create_user("member", email="member@example.com")
    obj_in = ChannelCreate(name="Team", channel_type="community")
    channel = svc.create_channel(db_session, obj_in, created_by=owner.id)
    svc.add_member(db_session, channel.id, member.id, role="member")
    updated = svc.update_member_role(db_session, channel.id, member.id, "moderator")
    assert updated.role == "moderator"


def test_update_member_role_raises_404_if_not_found(db_session, create_user):
    owner = create_user("owner")
    obj_in = ChannelCreate(name="Team", channel_type="community")
    channel = svc.create_channel(db_session, obj_in, created_by=owner.id)
    with pytest.raises(HTTPException) as exc:
        svc.update_member_role(db_session, channel.id, 999, "moderator")
    assert exc.value.status_code == 404
