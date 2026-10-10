from app.services.group_service import (
    RoleGroupService,
    RoleGroupMembershipService,
    CommitteeService,
    CommitteeMemberService,
    RoleDelegationService,
    RoleTransitionService,
)
from app.schemas.role_group import RoleGroupCreate, RoleGroupMembershipCreate
from app.schemas.committee import CommitteeCreate, CommitteeMemberCreate
from app.schemas.role_delegation import RoleDelegationCreate


class TestRoleGroupService:
    def setup_method(self):
        self.svc = RoleGroupService()

    def test_create(self, db_session):
        obj_in = RoleGroupCreate(name="direction", display_name="Direccion")
        result = self.svc.create(db_session, obj_in)
        assert result.id is not None
        assert result.name == "direction"
        assert result.display_name == "Direccion"
        assert result.is_active is True
        assert result.sort_order == 0

    def test_get_by_name_found(self, db_session):
        obj_in = RoleGroupCreate(name="technical", display_name="Tecnica")
        created = self.svc.create(db_session, obj_in)
        result = self.svc.get_by_name(db_session, "technical")
        assert result is not None
        assert result.id == created.id
        assert result.name == "technical"

    def test_get_by_name_not_found(self, db_session):
        result = self.svc.get_by_name(db_session, "nonexistent")
        assert result is None

    def test_get_active(self, db_session):
        self.svc.create(
            db_session, RoleGroupCreate(name="group_a", display_name="Group A", is_active=True, sort_order=0)
        )  # noqa: E501
        self.svc.create(
            db_session, RoleGroupCreate(name="group_b", display_name="Group B", is_active=False, sort_order=1)
        )  # noqa: E501
        self.svc.create(
            db_session, RoleGroupCreate(name="group_c", display_name="Group C", is_active=True, sort_order=2)
        )  # noqa: E501
        active = self.svc.get_active(db_session)
        assert len(active) == 2
        assert active[0].name == "group_a"
        assert active[1].name == "group_c"

    def test_get_all_paginated_no_filter(self, db_session):
        for i in range(5):
            self.svc.create(db_session, RoleGroupCreate(name=f"group_{i}", display_name=f"Group {i}", sort_order=i))
        result = self.svc.get_all_paginated(db_session, page=1, size=2)
        assert result["total"] == 5
        assert len(result["items"]) == 2
        assert result["page"] == 1
        assert result["size"] == 2
        assert result["pages"] == 3

    def test_get_all_paginated_filter_active(self, db_session):
        self.svc.create(db_session, RoleGroupCreate(name="g1", display_name="G1", is_active=True, sort_order=0))
        self.svc.create(db_session, RoleGroupCreate(name="g2", display_name="G2", is_active=False, sort_order=1))
        self.svc.create(db_session, RoleGroupCreate(name="g3", display_name="G3", is_active=True, sort_order=2))
        result = self.svc.get_all_paginated(db_session, page=1, size=10, is_active=True)
        assert result["total"] == 2
        result_inactive = self.svc.get_all_paginated(db_session, page=1, size=10, is_active=False)
        assert result_inactive["total"] == 1


class TestRoleGroupMembershipService:
    def setup_method(self):
        self.svc = RoleGroupMembershipService()

    def test_create(self, db_session, create_role, create_festival):
        group_svc = RoleGroupService()
        group = group_svc.create(db_session, RoleGroupCreate(name="test_group", display_name="Test Group"))
        role = create_role(name="test_role", display_name="Test Role")
        obj_in = RoleGroupMembershipCreate(group_id=group.id, role_id=role.id, level=10, is_leader=True)
        result = self.svc.create(db_session, obj_in)
        assert result.id is not None
        assert result.group_id == group.id
        assert result.role_id == role.id
        assert result.level == 10
        assert result.is_leader is True
        assert result.is_active is True

    def test_get_by_group(self, db_session, create_role):
        group_svc = RoleGroupService()
        group = group_svc.create(db_session, RoleGroupCreate(name="g", display_name="G"))
        role = create_role()
        self.svc.create(
            db_session, RoleGroupMembershipCreate(group_id=group.id, role_id=role.id, level=5, is_leader=False)
        )  # noqa: E501
        self.svc.create(
            db_session, RoleGroupMembershipCreate(group_id=group.id, role_id=role.id, level=10, is_leader=True)
        )  # noqa: E501
        members = self.svc.get_by_group(db_session, group.id)
        assert len(members) == 2
        assert members[0].level >= members[1].level

    def test_get_by_group_paginated(self, db_session, create_role):
        group_svc = RoleGroupService()
        group = group_svc.create(db_session, RoleGroupCreate(name="g", display_name="G"))
        role = create_role()
        for i in range(4):
            self.svc.create(db_session, RoleGroupMembershipCreate(group_id=group.id, role_id=role.id, level=i))
        result = self.svc.get_by_group_paginated(db_session, group.id, page=1, size=2)
        assert result["total"] == 4
        assert len(result["items"]) == 2

    def test_get_leaders(self, db_session, create_role):
        group_svc = RoleGroupService()
        group = group_svc.create(db_session, RoleGroupCreate(name="g", display_name="G"))
        role = create_role()
        leader = self.svc.create(
            db_session, RoleGroupMembershipCreate(group_id=group.id, role_id=role.id, level=10, is_leader=True)
        )  # noqa: E501
        self.svc.create(
            db_session, RoleGroupMembershipCreate(group_id=group.id, role_id=role.id, level=5, is_leader=False)
        )  # noqa: E501
        leaders = self.svc.get_leaders(db_session, group.id)
        assert len(leaders) == 1
        assert leaders[0].id == leader.id


class TestCommitteeService:
    def setup_method(self):
        self.svc = CommitteeService()

    def test_create(self, db_session, create_festival):
        festival = create_festival()
        obj_in = CommitteeCreate(festival_id=festival.id, name="Selection Committee")
        result = self.svc.create(db_session, obj_in)
        assert result.id is not None
        assert result.festival_id == festival.id
        assert result.name == "Selection Committee"
        assert result.is_active is True

    def test_get_by_festival(self, db_session, create_festival):
        f1 = create_festival(name="Fest A")
        f2 = create_festival(name="Fest B")
        c1 = self.svc.create(db_session, CommitteeCreate(festival_id=f1.id, name="Committee 1"))
        self.svc.create(db_session, CommitteeCreate(festival_id=f2.id, name="Committee 2"))
        committees = self.svc.get_by_festival(db_session, f1.id)
        assert len(committees) == 1
        assert committees[0].id == c1.id

    def test_get_by_festival_paginated(self, db_session, create_festival):
        festival = create_festival()
        for i in range(4):
            self.svc.create(db_session, CommitteeCreate(festival_id=festival.id, name=f"Committee {i}"))
        result = self.svc.get_by_festival_paginated(db_session, festival.id, page=1, size=2)
        assert result["total"] == 4
        assert len(result["items"]) == 2

    def test_get_member_count(self, db_session, create_festival, create_user):
        festival = create_festival()
        committee = self.svc.create(db_session, CommitteeCreate(festival_id=festival.id, name="Test Committee"))
        user = create_user()
        mem_svc = CommitteeMemberService()
        mem_svc.create(db_session, CommitteeMemberCreate(committee_id=committee.id, user_id=user.id))
        count = self.svc.get_member_count(db_session, committee.id)
        assert count == 1

    def test_get_member_count_inactive_excluded(self, db_session, create_festival, create_user):
        festival = create_festival()
        committee = self.svc.create(db_session, CommitteeCreate(festival_id=festival.id, name="Test Committee"))
        user = create_user()
        mem_svc = CommitteeMemberService()
        member = mem_svc.create(db_session, CommitteeMemberCreate(committee_id=committee.id, user_id=user.id))
        count_active = self.svc.get_member_count(db_session, committee.id)
        assert count_active == 1
        from app.schemas.committee import CommitteeMemberUpdate

        mem_svc.update(db_session, member.id, CommitteeMemberUpdate(is_active=False))
        count_after = self.svc.get_member_count(db_session, committee.id)
        assert count_after == 0


class TestCommitteeMemberService:
    def setup_method(self):
        self.svc = CommitteeMemberService()

    def test_get_by_committee(self, db_session, create_festival, create_user):
        committee_svc = CommitteeService()
        festival = create_festival()
        committee = committee_svc.create(db_session, CommitteeCreate(festival_id=festival.id, name="C"))
        user1 = create_user(username="user1")
        user2 = create_user(username="user2", email="user2@test.com")
        m1 = self.svc.create(db_session, CommitteeMemberCreate(committee_id=committee.id, user_id=user1.id))
        m2 = self.svc.create(db_session, CommitteeMemberCreate(committee_id=committee.id, user_id=user2.id))
        members = self.svc.get_by_committee(db_session, committee.id)
        assert len(members) == 2
        member_ids = {m.id for m in members}
        assert m1.id in member_ids
        assert m2.id in member_ids

    def test_get_membership_found(self, db_session, create_festival, create_user):
        committee_svc = CommitteeService()
        festival = create_festival()
        committee = committee_svc.create(db_session, CommitteeCreate(festival_id=festival.id, name="C"))
        user = create_user()
        member = self.svc.create(db_session, CommitteeMemberCreate(committee_id=committee.id, user_id=user.id))
        result = self.svc.get_membership(db_session, committee.id, user.id)
        assert result is not None
        assert result.id == member.id

    def test_get_membership_not_found(self, db_session, create_festival, create_user):
        committee_svc = CommitteeService()
        festival = create_festival()
        committee = committee_svc.create(db_session, CommitteeCreate(festival_id=festival.id, name="C"))
        user = create_user()
        result = self.svc.get_membership(db_session, committee.id, user.id)
        assert result is None


class TestRoleDelegationService:
    def setup_method(self):
        self.svc = RoleDelegationService()

    def test_create(self, db_session, create_user, create_role):
        u1 = create_user(username="delegator")
        u2 = create_user(username="delegate", email="delegate@test.com")
        role = create_role()
        obj_in = RoleDelegationCreate(delegator_id=u1.id, delegate_id=u2.id, role_id=role.id, reason="Coverage")
        result = self.svc.create(db_session, obj_in)
        assert result.id is not None
        assert result.delegator_id == u1.id
        assert result.delegate_id == u2.id
        assert result.role_id == role.id
        assert result.status == "active"
        assert result.reason == "Coverage"

    def test_get_all_paginated_no_filter(self, db_session, create_user, create_role):
        u1 = create_user(username="u1")
        u2 = create_user(username="u2", email="u2@test.com")
        role = create_role()
        for _ in range(4):
            self.svc.create(db_session, RoleDelegationCreate(delegator_id=u1.id, delegate_id=u2.id, role_id=role.id))
        result = self.svc.get_all_paginated(db_session, page=1, size=2)
        assert result["total"] == 4
        assert len(result["items"]) == 2

    def test_get_all_paginated_filter_delegator(self, db_session, create_user, create_role):
        u1 = create_user(username="u1")
        u2 = create_user(username="u2", email="u2@test.com")
        create_user(username="u3", email="u3@test.com")
        role = create_role()
        self.svc.create(db_session, RoleDelegationCreate(delegator_id=u1.id, delegate_id=u2.id, role_id=role.id))
        self.svc.create(db_session, RoleDelegationCreate(delegator_id=u2.id, delegate_id=u1.id, role_id=role.id))
        result = self.svc.get_all_paginated(db_session, page=1, size=10, delegator_id=u1.id)
        assert result["total"] == 1

    def test_get_all_paginated_filter_delegate(self, db_session, create_user, create_role):
        u1 = create_user(username="u1")
        u2 = create_user(username="u2", email="u2@test.com")
        role = create_role()
        self.svc.create(db_session, RoleDelegationCreate(delegator_id=u1.id, delegate_id=u2.id, role_id=role.id))
        self.svc.create(db_session, RoleDelegationCreate(delegator_id=u2.id, delegate_id=u1.id, role_id=role.id))
        result = self.svc.get_all_paginated(db_session, page=1, size=10, delegate_id=u2.id)
        assert result["total"] == 1

    def test_get_all_paginated_filter_status(self, db_session, create_user, create_role):
        u1 = create_user(username="u1")
        u2 = create_user(username="u2", email="u2@test.com")
        role = create_role()
        d1 = self.svc.create(
            db_session, RoleDelegationCreate(delegator_id=u1.id, delegate_id=u2.id, role_id=role.id, status="active")
        )  # noqa: E501
        self.svc.revoke(db_session, d1.id, u1.id)
        result_active = self.svc.get_all_paginated(db_session, page=1, size=10, status="active")
        assert result_active["total"] == 0
        result_revoked = self.svc.get_all_paginated(db_session, page=1, size=10, status="revoked")
        assert result_revoked["total"] == 1

    def test_get_active_by_delegator(self, db_session, create_user, create_role):
        u1 = create_user(username="delegator")
        u2 = create_user(username="delegate", email="delegate@test.com")
        role = create_role()
        active = self.svc.create(
            db_session, RoleDelegationCreate(delegator_id=u1.id, delegate_id=u2.id, role_id=role.id)
        )  # noqa: E501
        result = self.svc.get_active_by_delegator(db_session, u1.id)
        assert len(result) == 1
        assert result[0].id == active.id

    def test_get_active_by_delegate(self, db_session, create_user, create_role):
        u1 = create_user(username="delegator")
        u2 = create_user(username="delegate", email="delegate@test.com")
        role = create_role()
        active = self.svc.create(
            db_session, RoleDelegationCreate(delegator_id=u1.id, delegate_id=u2.id, role_id=role.id)
        )  # noqa: E501
        result = self.svc.get_active_by_delegate(db_session, u2.id)
        assert len(result) == 1
        assert result[0].id == active.id

    def test_revoke(self, db_session, create_user, create_role):
        u1 = create_user(username="u1")
        u2 = create_user(username="u2", email="u2@test.com")
        role = create_role()
        delegation = self.svc.create(
            db_session, RoleDelegationCreate(delegator_id=u1.id, delegate_id=u2.id, role_id=role.id)
        )  # noqa: E501
        revoked = self.svc.revoke(db_session, delegation.id, revoked_by=u1.id, reason="No longer needed")
        assert revoked is not None
        assert revoked.status == "revoked"
        assert revoked.revoked_by == u1.id
        assert revoked.revoked_reason == "No longer needed"
        assert revoked.revoked_at is not None

    def test_revoke_nonexistent(self, db_session, create_user):
        u1 = create_user()
        result = self.svc.revoke(db_session, 999, revoked_by=u1.id)
        assert result is None


class TestRoleTransitionService:
    def setup_method(self):
        self.svc = RoleTransitionService()

    def test_record_transition(self, db_session, create_user, create_role):
        user = create_user()
        role = create_role()
        result = self.svc.record_transition(
            db_session,
            user_id=user.id,
            to_role_id=role.id,
            transition_type="promotion",
            changed_by=user.id,
            reason="Promoted to new role",
        )
        assert result.id is not None
        assert result.user_id == user.id
        assert result.to_role_id == role.id
        assert result.transition_type == "promotion"
        assert result.changed_by == user.id
        assert result.reason == "Promoted to new role"

    def test_record_transition_with_from(self, db_session, create_user, create_role):
        user = create_user()
        from_role = create_role(name="from_role", display_name="From Role", hierarchy_level=30)
        to_role = create_role(name="to_role", display_name="To Role", hierarchy_level=50)
        result = self.svc.record_transition(
            db_session,
            user_id=user.id,
            to_role_id=to_role.id,
            transition_type="promotion",
            changed_by=user.id,
            from_role_id=from_role.id,
            reason="Promotion",
        )
        assert result.from_role_id == from_role.id
        assert result.to_role_id == to_role.id

    def test_get_by_user(self, db_session, create_user, create_role):
        user = create_user()
        user2 = create_user(username="other", email="other@test.com")
        role = create_role()
        self.svc.record_transition(
            db_session,
            user_id=user.id,
            to_role_id=role.id,
            transition_type="creation",
            changed_by=user.id,
        )
        self.svc.record_transition(
            db_session,
            user_id=user2.id,
            to_role_id=role.id,
            transition_type="creation",
            changed_by=user2.id,
        )
        transitions = self.svc.get_by_user(db_session, user.id)
        assert len(transitions) == 1

    def test_get_by_festival(self, db_session, create_user, create_role, create_festival):
        user = create_user()
        role = create_role()
        festival = create_festival()
        self.svc.record_transition(
            db_session,
            user_id=user.id,
            to_role_id=role.id,
            transition_type="transfer",
            changed_by=user.id,
            to_festival_id=festival.id,
        )
        transitions = self.svc.get_by_festival(db_session, festival.id)
        assert len(transitions) == 1

    def test_get_all_paginated_no_filter(self, db_session, create_user, create_role):
        user = create_user()
        role = create_role()
        for _ in range(4):
            self.svc.record_transition(
                db_session,
                user_id=user.id,
                to_role_id=role.id,
                transition_type="creation",
                changed_by=user.id,
            )
        result = self.svc.get_all_paginated(db_session, page=1, size=2)
        assert result["total"] == 4
        assert len(result["items"]) == 2

    def test_get_all_paginated_filter_user(self, db_session, create_user, create_role):
        u1 = create_user()
        u2 = create_user(username="u2", email="u2@test.com")
        role = create_role()
        self.svc.record_transition(
            db_session,
            user_id=u1.id,
            to_role_id=role.id,
            transition_type="creation",
            changed_by=u1.id,
        )
        self.svc.record_transition(
            db_session,
            user_id=u2.id,
            to_role_id=role.id,
            transition_type="creation",
            changed_by=u2.id,
        )
        result = self.svc.get_all_paginated(db_session, page=1, size=10, user_id=u1.id)
        assert result["total"] == 1

    def test_get_all_paginated_filter_transition_type(self, db_session, create_user, create_role):
        user = create_user()
        role = create_role()
        self.svc.record_transition(
            db_session,
            user_id=user.id,
            to_role_id=role.id,
            transition_type="creation",
            changed_by=user.id,
        )
        self.svc.record_transition(
            db_session,
            user_id=user.id,
            to_role_id=role.id,
            transition_type="promotion",
            changed_by=user.id,
        )
        result = self.svc.get_all_paginated(db_session, page=1, size=10, transition_type="creation")
        assert result["total"] == 1
