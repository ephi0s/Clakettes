"""Role service — business logic for roles, dependencies, conflicts, and festival roles."""

from sqlalchemy.orm import Session
from app.models.role import Role, FestivalRole, RoleScope, RoleDependency, RoleConflict
from app.models.user_role import UserRole, UserRoleStatus
from app.schemas.role import RoleCreate, RoleUpdate, FestivalRoleCreate, FestivalRoleUpdate
from app.schemas.user_role import UserRoleCreate, UserRoleUpdate
from .base_service import BaseService


class RoleService(BaseService[Role, RoleCreate, RoleUpdate]):
    def __init__(self):
        super().__init__(Role)

    def get_by_name(self, db: Session, name: str) -> Role | None:
        return db.query(Role).filter(Role.name == name).first()

    def get_global_roles(self, db: Session) -> list[Role]:
        return db.query(Role).filter(Role.scope == RoleScope.GLOBAL).order_by(Role.hierarchy_level.desc()).all()

    def get_festival_roles(self, db: Session, festival_id: int) -> list[FestivalRole]:
        return db.query(FestivalRole).filter(FestivalRole.festival_id == festival_id, FestivalRole.is_active).all()

    def get_role_hierarchy(self, db: Session) -> list[Role]:
        """Get all roles organized as a tree (parents first)."""
        return db.query(Role).filter(Role.parent_role_id.is_(None)).order_by(Role.hierarchy_level.desc()).all()

    def get_all(self, db: Session, scope: str | None = None) -> list:
        query = db.query(Role)
        if scope:
            query = query.filter(Role.scope == RoleScope(scope))
        return query.all()

    def get_all_paginated(self, db: Session, page: int, size: int, scope: str | None = None) -> dict:
        filters = []
        if scope:
            filters.append(Role.scope == RoleScope(scope))
        return self.paginate_filtered(db, page, size, *filters)

    def get_all_ordered_by_hierarchy(self, db: Session) -> list:
        return db.query(Role).order_by(Role.hierarchy_level.desc()).all()

    def can_assign_role(self, db: Session, assigner_user_id: int, role_id: int, festival_id: int | None = None) -> bool:
        """Check if a user can assign a specific role."""
        role = self.get(db, role_id)
        if not role:
            return False

        # Admin can assign any role marked as assignable_by_admin
        # In practice, check if user has admin role
        # For now, return based on role config
        return role.is_assignable_by_admin

    def create_festival_role(self, db: Session, obj_in: FestivalRoleCreate) -> FestivalRole:
        # Check if role already exists for this festival
        existing = (
            db.query(FestivalRole)
            .filter(FestivalRole.festival_id == obj_in.festival_id, FestivalRole.role_id == obj_in.role_id)
            .first()
        )
        if existing:
            # Update existing
            for field, value in obj_in.model_dump().items():
                setattr(existing, field, value)
            db.commit()
            db.refresh(existing)
            return existing

        db_obj = FestivalRole(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class FestivalRoleService(BaseService[FestivalRole, FestivalRoleCreate, FestivalRoleUpdate]):
    def __init__(self):
        super().__init__(FestivalRole)

    def get_by_festival_and_role(self, db: Session, festival_id: int, role_id: int) -> FestivalRole | None:
        return (
            db.query(FestivalRole)
            .filter(FestivalRole.festival_id == festival_id, FestivalRole.role_id == role_id)
            .first()
        )

    def get_active_for_festival(self, db: Session, festival_id: int) -> list[FestivalRole]:
        return db.query(FestivalRole).filter(FestivalRole.festival_id == festival_id, FestivalRole.is_active).all()

    def get_by_festival_paginated(self, db: Session, festival_id: int, page: int, size: int) -> dict:
        from sqlalchemy.orm import joinedload

        query = db.query(FestivalRole).filter(FestivalRole.festival_id == festival_id)
        return self.paginate(query.options(joinedload(FestivalRole.role)), page, size)

    def initialize_default_festival_roles(self, db: Session, festival_id: int) -> list[FestivalRole]:
        """Create default festival-scoped roles for a new festival."""
        role_service = RoleService()
        default_roles = [
            {"name": "organizer", "display_name": "Organizador", "hierarchy_level": 100, "scope": RoleScope.FESTIVAL},
            {
                "name": "programmer",
                "display_name": "Programador/Curador",
                "hierarchy_level": 80,
                "scope": RoleScope.FESTIVAL,
            },
            {"name": "jury", "display_name": "Jurado", "hierarchy_level": 70, "scope": RoleScope.FESTIVAL},
            {"name": "technician", "display_name": "Staff Técnico", "hierarchy_level": 60, "scope": RoleScope.FESTIVAL},
            {"name": "hospitality", "display_name": "Hospitalidad", "hierarchy_level": 50, "scope": RoleScope.FESTIVAL},
            {"name": "security", "display_name": "Seguridad", "hierarchy_level": 50, "scope": RoleScope.FESTIVAL},
            {
                "name": "marketing",
                "display_name": "Marketing/Comunicación",
                "hierarchy_level": 50,
                "scope": RoleScope.FESTIVAL,
            },
            {"name": "finance", "display_name": "Finanzas", "hierarchy_level": 50, "scope": RoleScope.FESTIVAL},
            {
                "name": "accessibility",
                "display_name": "Coordinador de Accesibilidad",
                "hierarchy_level": 50,
                "scope": RoleScope.FESTIVAL,
            },
            {"name": "volunteer", "display_name": "Voluntario", "hierarchy_level": 10, "scope": RoleScope.FESTIVAL},
            {"name": "press", "display_name": "Prensa Acreditada", "hierarchy_level": 40, "scope": RoleScope.FESTIVAL},
            {"name": "critic", "display_name": "Crítico", "hierarchy_level": 40, "scope": RoleScope.FESTIVAL},
            {
                "name": "agent",
                "display_name": "Agente/Representante",
                "hierarchy_level": 40,
                "scope": RoleScope.FESTIVAL,
            },
            {
                "name": "exhibitor",
                "display_name": "Vendedor/Expositor",
                "hierarchy_level": 30,
                "scope": RoleScope.FESTIVAL,
            },
            {
                "name": "student",
                "display_name": "Estudiante Acreditado",
                "hierarchy_level": 10,
                "scope": RoleScope.FESTIVAL,
            },
        ]

        created = []
        for role_data in default_roles:
            role = role_service.get_by_name(db, role_data["name"])
            if not role:
                role = Role(**role_data)
                db.add(role)
                db.commit()
                db.refresh(role)

            festival_role = self.get_by_festival_and_role(db, festival_id, role.id)
            if not festival_role:
                festival_role = FestivalRole(festival_id=festival_id, role_id=role.id)
                db.add(festival_role)
                created.append(festival_role)

        db.commit()
        for fr in created:
            db.refresh(fr)
        return created

    # ===========================
    # Role Dependencies
    # ===========================

    def get_dependencies(self, db: Session, role_id: int) -> list[RoleDependency]:
        return db.query(RoleDependency).filter(RoleDependency.role_id == role_id).all()

    def get_dependents(self, db: Session, role_id: int) -> list[RoleDependency]:
        """Roles that depend on this role."""
        return db.query(RoleDependency).filter(RoleDependency.depends_on_role_id == role_id).all()

    def add_dependency(
        self,
        db: Session,
        role_id: int,
        depends_on_role_id: int,
        dependency_type: str = "required",
        notes: str | None = None,
    ) -> RoleDependency:
        existing = (
            db.query(RoleDependency)
            .filter(
                RoleDependency.role_id == role_id,
                RoleDependency.depends_on_role_id == depends_on_role_id,
            )
            .first()
        )
        if existing:
            existing.dependency_type = dependency_type
            if notes:
                existing.notes = notes
            db.commit()
            db.refresh(existing)
            return existing
        dep = RoleDependency(
            role_id=role_id, depends_on_role_id=depends_on_role_id, dependency_type=dependency_type, notes=notes
        )
        db.add(dep)
        db.commit()
        db.refresh(dep)
        return dep

    def remove_dependency(self, db: Session, dependency_id: int) -> bool:
        dep = db.query(RoleDependency).filter(RoleDependency.id == dependency_id).first()
        if dep:
            db.delete(dep)
            db.commit()
            return True
        return False

    def check_fulfilled_dependencies(self, db: Session, user_id: int, role_id: int) -> list[dict]:
        """Check if a user fulfills all dependencies for a role."""
        from app.models.user_role import UserRole

        deps = self.get_dependencies(db, role_id)
        results = []
        for dep in deps:
            has_role = (
                db.query(UserRole)
                .filter(
                    UserRole.user_id == user_id,
                    UserRole.role_id == dep.depends_on_role_id,
                    UserRole.status.in_([UserRoleStatus.APPROVED.value, UserRoleStatus.ACTIVE.value]),
                )
                .first()
            )
            results.append(
                {
                    "dependency_id": dep.id,
                    "depends_on_role_id": dep.depends_on_role_id,
                    "dependency_type": dep.dependency_type,
                    "fulfilled": has_role is not None,
                }
            )
        return results

    # ===========================
    # Role Conflicts
    # ===========================

    def get_conflicts(self, db: Session, role_id: int) -> list[RoleConflict]:
        return db.query(RoleConflict).filter(RoleConflict.role_id == role_id).all()

    def get_conflicting_roles(self, db: Session, role_id: int) -> list[RoleConflict]:
        """Roles that conflict with this role (either direction)."""
        return (
            db.query(RoleConflict)
            .filter(
                (RoleConflict.role_id == role_id) | (RoleConflict.conflicts_with_role_id == role_id),
            )
            .all()
        )

    def add_conflict(
        self,
        db: Session,
        role_id: int,
        conflicts_with_role_id: int,
        conflict_type: str = "exclusive",
        notes: str | None = None,
    ) -> RoleConflict:
        existing = (
            db.query(RoleConflict)
            .filter(
                RoleConflict.role_id == role_id,
                RoleConflict.conflicts_with_role_id == conflicts_with_role_id,
            )
            .first()
        )
        if existing:
            existing.conflict_type = conflict_type
            if notes:
                existing.notes = notes
            db.commit()
            db.refresh(existing)
            return existing
        conflict = RoleConflict(
            role_id=role_id, conflicts_with_role_id=conflicts_with_role_id, conflict_type=conflict_type, notes=notes
        )
        db.add(conflict)
        db.commit()
        db.refresh(conflict)
        return conflict

    def remove_conflict(self, db: Session, conflict_id: int) -> bool:
        conflict = db.query(RoleConflict).filter(RoleConflict.id == conflict_id).first()
        if conflict:
            db.delete(conflict)
            db.commit()
            return True
        return False

    def check_role_conflicts(self, db: Session, user_id: int, role_id: int) -> list[dict]:
        """Check if assigning this role would cause conflicts with existing user roles."""
        from app.models.user_role import UserRole

        conflicts = self.get_conflicting_roles(db, role_id)
        results = []
        for c in conflicts:
            conflicting_id = c.conflicts_with_role_id if c.role_id == role_id else c.role_id
            has_role = (
                db.query(UserRole)
                .filter(
                    UserRole.user_id == user_id,
                    UserRole.role_id == conflicting_id,
                    UserRole.status.in_([UserRoleStatus.APPROVED.value, UserRoleStatus.ACTIVE.value]),
                )
                .first()
            )
            if has_role:
                results.append(
                    {
                        "conflict_id": c.id,
                        "existing_role_id": conflicting_id,
                        "conflict_type": c.conflict_type,
                        "message": f"Role conflict: user already has role #{conflicting_id}",
                    }
                )
        return results


class UserRoleService(BaseService[UserRole, UserRoleCreate, UserRoleUpdate]):
    def __init__(self):
        super().__init__(UserRole)

    def get_by_user(
        self, db: Session, user_id: int, festival_id: int | None = None, include_hidden: bool = False
    ) -> list:
        from sqlalchemy.orm import joinedload

        query = db.query(UserRole).filter(UserRole.user_id == user_id)
        if festival_id:
            query = query.filter(UserRole.festival_id == festival_id)
        if not include_hidden:
            query = query.filter(~UserRole.is_hidden)
        return query.options(joinedload(UserRole.role)).all()

    def get_by_user_in_festivals(
        self, db: Session, user_id: int, festival_ids: list[int], include_hidden: bool = False
    ) -> list:
        from sqlalchemy.orm import joinedload

        if not festival_ids:
            return []
        query = db.query(UserRole).filter(UserRole.user_id == user_id, UserRole.festival_id.in_(festival_ids))
        if not include_hidden:
            query = query.filter(~UserRole.is_hidden)
        return query.options(joinedload(UserRole.role)).order_by(UserRole.festival_id, UserRole.id).all()

    def get_by_user_paginated(
        self,
        db: Session,
        user_id: int,
        page: int,
        size: int,
        festival_id: int | None = None,
        include_hidden: bool = False,
    ) -> dict:
        from sqlalchemy.orm import joinedload

        query = db.query(UserRole).filter(UserRole.user_id == user_id)
        if festival_id:
            query = query.filter(UserRole.festival_id == festival_id)
        if not include_hidden:
            query = query.filter(~UserRole.is_hidden)
        return self.paginate(query.options(joinedload(UserRole.role)), page, size)

    def get_by_festival(self, db: Session, festival_id: int) -> list:
        return db.query(UserRole).filter(UserRole.festival_id == festival_id).all()
