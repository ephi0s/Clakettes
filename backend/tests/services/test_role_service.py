from app.services.role_service import RoleService, FestivalRoleService, UserRoleService
from app.models.role import FestivalRole, RoleDependency, RoleConflict
from app.models.user_role import UserRole, UserRoleStatus
from app.schemas.role import FestivalRoleCreate


class TestRoleService:
    def setup_method(self):
        self.service = RoleService()

    def test_get_by_name_found(self, db_session, create_role):
        create_role(name="admin", display_name="Admin", hierarchy_level=100, scope="global")
        result = self.service.get_by_name(db_session, "admin")
        assert result is not None
        assert result.name == "admin"

    def test_get_by_name_not_found(self, db_session):
        result = self.service.get_by_name(db_session, "nonexistent")
        assert result is None

    def test_get_global_roles(self, db_session, create_role):
        create_role(name="global1", hierarchy_level=50, scope="global")
        create_role(name="global2", hierarchy_level=100, scope="global")
        create_role(name="fest_role", scope="festival")
        result = self.service.get_global_roles(db_session)
        assert len(result) == 2
        assert result[0].hierarchy_level >= result[1].hierarchy_level

    def test_get_festival_roles(self, db_session, create_role, create_festival):
        festival = create_festival()
        role = create_role()
        fr = FestivalRole(festival_id=festival.id, role_id=role.id, is_active=True)
        db_session.add(fr)
        db_session.commit()
        inactive = FestivalRole(festival_id=festival.id, role_id=role.id, is_active=False)
        db_session.add(inactive)
        db_session.commit()
        result = self.service.get_festival_roles(db_session, festival_id=festival.id)
        assert len(result) == 1
        assert result[0].is_active is True

    def test_get_role_hierarchy(self, db_session, create_role):
        parent = create_role(name="parent", hierarchy_level=100)
        child = create_role(name="child", hierarchy_level=50)
        child.parent_role_id = parent.id
        db_session.commit()
        result = self.service.get_role_hierarchy(db_session)
        assert len(result) == 1
        assert result[0].name == "parent"

    def test_get_all_no_filter(self, db_session, create_role):
        create_role(name="r1", scope="global")
        create_role(name="r2", scope="festival")
        result = self.service.get_all(db_session)
        assert len(result) == 2

    def test_get_all_filter_by_scope(self, db_session, create_role):
        create_role(name="global_role", scope="global")
        create_role(name="fest_role", scope="festival")
        result = self.service.get_all(db_session, scope="festival")
        assert len(result) == 1
        assert result[0].name == "fest_role"

    def test_get_all_ordered_by_hierarchy(self, db_session, create_role):
        create_role(name="low", hierarchy_level=10)
        create_role(name="high", hierarchy_level=100)
        create_role(name="mid", hierarchy_level=50)
        result = self.service.get_all_ordered_by_hierarchy(db_session)
        assert len(result) == 3
        assert [r.name for r in result] == ["high", "mid", "low"]

    def test_can_assign_role_returns_true_when_assignable(self, db_session, create_role):
        role = create_role(name="assignable_role")
        role.is_assignable_by_admin = True
        db_session.commit()
        result = self.service.can_assign_role(db_session, assigner_user_id=1, role_id=role.id)
        assert result is True

    def test_can_assign_role_returns_false_when_not_assignable(self, db_session, create_role):
        role = create_role(name="restricted_role")
        role.is_assignable_by_admin = False
        db_session.commit()
        result = self.service.can_assign_role(db_session, assigner_user_id=1, role_id=role.id)
        assert result is False

    def test_can_assign_role_returns_false_when_role_not_found(self, db_session):
        result = self.service.can_assign_role(db_session, assigner_user_id=1, role_id=999)
        assert result is False

    def test_create_festival_role_creates_new(self, db_session, create_role, create_festival):
        festival = create_festival()
        role = create_role()
        obj_in = FestivalRoleCreate(festival_id=festival.id, role_id=role.id)
        result = self.service.create_festival_role(db_session, obj_in)
        assert result.festival_id == festival.id
        assert result.role_id == role.id
        assert result.is_active is True

    def test_create_festival_role_updates_existing(self, db_session, create_role, create_festival):
        festival = create_festival()
        role = create_role()
        fr = FestivalRole(festival_id=festival.id, role_id=role.id, is_active=True)
        db_session.add(fr)
        db_session.commit()
        obj_in = FestivalRoleCreate(festival_id=festival.id, role_id=role.id, is_active=False)
        result = self.service.create_festival_role(db_session, obj_in)
        assert result.is_active is False
        assert result.id == fr.id


class TestFestivalRoleService:
    def setup_method(self):
        self.service = FestivalRoleService()

    def test_get_by_festival_and_role_found(self, db_session, create_role, create_festival):
        festival = create_festival()
        role = create_role()
        fr = FestivalRole(festival_id=festival.id, role_id=role.id)
        db_session.add(fr)
        db_session.commit()
        result = self.service.get_by_festival_and_role(db_session, festival.id, role.id)
        assert result is not None
        assert result.festival_id == festival.id

    def test_get_by_festival_and_role_not_found(self, db_session):
        result = self.service.get_by_festival_and_role(db_session, festival_id=1, role_id=1)
        assert result is None

    def test_get_active_for_festival(self, db_session, create_role, create_festival):
        festival = create_festival()
        role = create_role()
        active = FestivalRole(festival_id=festival.id, role_id=role.id, is_active=True)
        inactive = FestivalRole(festival_id=festival.id, role_id=role.id, is_active=False)
        db_session.add_all([active, inactive])
        db_session.commit()
        result = self.service.get_active_for_festival(db_session, festival.id)
        assert len(result) == 1
        assert result[0].is_active is True

    def test_get_by_festival_paginated(self, db_session, create_role, create_festival):
        festival = create_festival()
        role = create_role()
        for _ in range(5):
            fr = FestivalRole(festival_id=festival.id, role_id=role.id)
            db_session.add(fr)
        db_session.commit()
        result = self.service.get_by_festival_paginated(db_session, festival.id, page=1, size=2)
        assert result["total"] == 5
        assert len(result["items"]) == 2

    def test_initialize_default_festival_roles_creates_15(self, db_session, create_festival):
        festival = create_festival()
        result = self.service.initialize_default_festival_roles(db_session, festival.id)
        assert len(result) == 15
        role_names = [fr.role.name for fr in result]
        assert "organizer" in role_names
        assert "jury" in role_names
        assert "volunteer" in role_names

    def test_initialize_default_festival_roles_idempotent(self, db_session, create_festival):
        festival = create_festival()
        self.service.initialize_default_festival_roles(db_session, festival.id)
        second = self.service.initialize_default_festival_roles(db_session, festival.id)
        assert len(second) == 0

    def test_add_dependency_creates_new(self, db_session, create_role):
        r1 = create_role(name="manager")
        r2 = create_role(name="employee")
        dep = self.service.add_dependency(db_session, role_id=r1.id, depends_on_role_id=r2.id)
        assert dep.role_id == r1.id
        assert dep.depends_on_role_id == r2.id
        assert dep.dependency_type == "required"

    def test_add_dependency_updates_existing(self, db_session, create_role):
        r1 = create_role(name="manager")
        r2 = create_role(name="employee")
        original = self.service.add_dependency(db_session, role_id=r1.id, depends_on_role_id=r2.id)
        updated = self.service.add_dependency(
            db_session, role_id=r1.id, depends_on_role_id=r2.id, dependency_type="recommended", notes="optional"
        )  # noqa: E501
        assert updated.id == original.id
        assert updated.dependency_type == "recommended"
        assert updated.notes == "optional"

    def test_remove_dependency_returns_true(self, db_session, create_role):
        r1 = create_role(name="a")
        r2 = create_role(name="b")
        dep = self.service.add_dependency(db_session, role_id=r1.id, depends_on_role_id=r2.id)
        assert self.service.remove_dependency(db_session, dep.id) is True
        assert db_session.query(RoleDependency).filter(RoleDependency.id == dep.id).first() is None

    def test_remove_dependency_returns_false_when_not_found(self, db_session):
        assert self.service.remove_dependency(db_session, 999) is False

    def test_get_dependencies(self, db_session, create_role):
        r1 = create_role(name="manager")
        r2 = create_role(name="employee")
        r3 = create_role(name="intern")
        self.service.add_dependency(db_session, role_id=r1.id, depends_on_role_id=r2.id)
        self.service.add_dependency(db_session, role_id=r1.id, depends_on_role_id=r3.id)
        deps = self.service.get_dependencies(db_session, r1.id)
        assert len(deps) == 2

    def test_get_dependents(self, db_session, create_role):
        r1 = create_role(name="manager")
        r2 = create_role(name="employee")
        r3 = create_role(name="intern")
        self.service.add_dependency(db_session, role_id=r2.id, depends_on_role_id=r1.id)
        self.service.add_dependency(db_session, role_id=r3.id, depends_on_role_id=r1.id)
        dependents = self.service.get_dependents(db_session, r1.id)
        assert len(dependents) == 2

    def test_check_fulfilled_dependencies_all_fulfilled(self, db_session, create_role, create_user):
        user = create_user()
        r1 = create_role(name="senior")
        r2 = create_role(name="junior")
        self.service.add_dependency(db_session, role_id=r1.id, depends_on_role_id=r2.id)
        ur = UserRole(user_id=user.id, role_id=r2.id, status=UserRoleStatus.APPROVED.value)
        db_session.add(ur)
        db_session.commit()
        results = self.service.check_fulfilled_dependencies(db_session, user.id, r1.id)
        assert len(results) == 1
        assert results[0]["fulfilled"] is True

    def test_check_fulfilled_dependencies_not_fulfilled(self, db_session, create_role, create_user):
        user = create_user()
        r1 = create_role(name="senior")
        r2 = create_role(name="junior")
        self.service.add_dependency(db_session, role_id=r1.id, depends_on_role_id=r2.id)
        results = self.service.check_fulfilled_dependencies(db_session, user.id, r1.id)
        assert len(results) == 1
        assert results[0]["fulfilled"] is False

    def test_add_conflict_creates_new(self, db_session, create_role):
        r1 = create_role(name="role_a")
        r2 = create_role(name="role_b")
        c = self.service.add_conflict(db_session, role_id=r1.id, conflicts_with_role_id=r2.id)
        assert c.role_id == r1.id
        assert c.conflicts_with_role_id == r2.id
        assert c.conflict_type == "exclusive"

    def test_add_conflict_updates_existing(self, db_session, create_role):
        r1 = create_role(name="role_a")
        r2 = create_role(name="role_b")
        original = self.service.add_conflict(db_session, role_id=r1.id, conflicts_with_role_id=r2.id)
        updated = self.service.add_conflict(
            db_session, role_id=r1.id, conflicts_with_role_id=r2.id, conflict_type="restricted", notes="limited"
        )  # noqa: E501
        assert updated.id == original.id
        assert updated.conflict_type == "restricted"
        assert updated.notes == "limited"

    def test_remove_conflict_returns_true(self, db_session, create_role):
        r1 = create_role(name="a")
        r2 = create_role(name="b")
        c = self.service.add_conflict(db_session, role_id=r1.id, conflicts_with_role_id=r2.id)
        assert self.service.remove_conflict(db_session, c.id) is True
        assert db_session.query(RoleConflict).filter(RoleConflict.id == c.id).first() is None

    def test_remove_conflict_returns_false_when_not_found(self, db_session):
        assert self.service.remove_conflict(db_session, 999) is False

    def test_get_conflicts(self, db_session, create_role):
        r1 = create_role(name="a")
        r2 = create_role(name="b")
        r3 = create_role(name="c")
        self.service.add_conflict(db_session, role_id=r1.id, conflicts_with_role_id=r2.id)
        self.service.add_conflict(db_session, role_id=r1.id, conflicts_with_role_id=r3.id)
        conflicts = self.service.get_conflicts(db_session, r1.id)
        assert len(conflicts) == 2

    def test_get_conflicting_roles(self, db_session, create_role):
        r1 = create_role(name="a")
        r2 = create_role(name="b")
        r3 = create_role(name="c")
        self.service.add_conflict(db_session, role_id=r1.id, conflicts_with_role_id=r2.id)
        self.service.add_conflict(db_session, role_id=r3.id, conflicts_with_role_id=r1.id)
        conflicts = self.service.get_conflicting_roles(db_session, r1.id)
        assert len(conflicts) == 2

    def test_check_role_conflicts_with_conflict(self, db_session, create_role, create_user):
        user = create_user()
        r1 = create_role(name="role_a")
        r2 = create_role(name="role_b")
        self.service.add_conflict(db_session, role_id=r1.id, conflicts_with_role_id=r2.id)
        ur = UserRole(user_id=user.id, role_id=r2.id, status=UserRoleStatus.ACTIVE.value)
        db_session.add(ur)
        db_session.commit()
        results = self.service.check_role_conflicts(db_session, user.id, r1.id)
        assert len(results) == 1
        assert results[0]["conflict_type"] == "exclusive"
        assert results[0]["existing_role_id"] == r2.id

    def test_check_role_conflicts_without_conflict(self, db_session, create_role, create_user):
        user = create_user()
        r1 = create_role(name="role_a")
        create_role(name="role_b")
        results = self.service.check_role_conflicts(db_session, user.id, r1.id)
        assert len(results) == 0


class TestUserRoleService:
    def setup_method(self):
        self.service = UserRoleService()

    def test_get_by_user_no_filter(self, db_session, create_user, create_role):
        user = create_user()
        role = create_role()
        ur1 = UserRole(user_id=user.id, role_id=role.id, is_hidden=False)
        ur2 = UserRole(user_id=user.id, role_id=role.id, is_hidden=False)
        db_session.add_all([ur1, ur2])
        db_session.commit()
        result = self.service.get_by_user(db_session, user.id)
        assert len(result) == 2

    def test_get_by_user_filters_hidden(self, db_session, create_user, create_role):
        user = create_user()
        role = create_role()
        visible = UserRole(user_id=user.id, role_id=role.id, is_hidden=False)
        hidden = UserRole(user_id=user.id, role_id=role.id, is_hidden=True)
        db_session.add_all([visible, hidden])
        db_session.commit()
        result = self.service.get_by_user(db_session, user.id)
        assert len(result) == 1

    def test_get_by_user_includes_hidden_when_requested(self, db_session, create_user, create_role):
        user = create_user()
        role = create_role()
        hidden = UserRole(user_id=user.id, role_id=role.id, is_hidden=True)
        db_session.add(hidden)
        db_session.commit()
        result = self.service.get_by_user(db_session, user.id, include_hidden=True)
        assert len(result) == 1

    def test_get_by_user_filters_by_festival(self, db_session, create_user, create_role, create_festival):
        user = create_user()
        role = create_role()
        f1 = create_festival(name="F1")
        f2 = create_festival(name="F2")
        ur1 = UserRole(user_id=user.id, role_id=role.id, festival_id=f1.id, is_hidden=False)
        ur2 = UserRole(user_id=user.id, role_id=role.id, festival_id=f2.id, is_hidden=False)
        db_session.add_all([ur1, ur2])
        db_session.commit()
        result = self.service.get_by_user(db_session, user.id, festival_id=f1.id)
        assert len(result) == 1
        assert result[0].festival_id == f1.id

    def test_get_by_festival(self, db_session, create_user, create_role, create_festival):
        user = create_user()
        role = create_role()
        f1 = create_festival(name="F1")
        f2 = create_festival(name="F2")
        ur1 = UserRole(user_id=user.id, role_id=role.id, festival_id=f1.id)
        ur2 = UserRole(user_id=user.id, role_id=role.id, festival_id=f2.id)
        db_session.add_all([ur1, ur2])
        db_session.commit()
        result = self.service.get_by_festival(db_session, f1.id)
        assert len(result) == 1
        assert result[0].festival_id == f1.id
