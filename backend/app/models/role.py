"""Role model — defines global platform roles with hierarchy and permissions."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.enums import RoleScope


class Role(BaseModel):
    """Global platform role with hierarchy level and permissions.

    Roles define what a user can do on the platform. They can be:
    - Global: Apply across all festivals (admin, producer, distributor, etc.)
    - Festival-scoped: Apply only within a specific festival (organizer, jury, etc.)

    Attributes:
        name: Unique role identifier (e.g., 'admin', 'organizer', 'jury')
        display_name: Human-readable name for UI
        description: Detailed description of role responsibilities
        scope: Whether role is global or festival-scoped
        hierarchy_level: Integer for permission hierarchy (higher = more permissions)
        parent_role_id: Self-referential FK for role inheritance
        is_assignable_by_admin: Whether admins can assign this role
        requires_approval: Whether assignment needs approval from parent role
        permissions: JSON string of permission scopes (e.g., 'festivals:read,users:write')
    """

    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    scope = Column(
        SQLEnum(RoleScope, values_callable=lambda x: [e.value for e in x]), nullable=False, default=RoleScope.FESTIVAL
    )
    hierarchy_level = Column(Integer, default=0)  # Higher = more permissions
    parent_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    group_id = Column(Integer, ForeignKey("role_groups.id"), nullable=True)  # Role group/category
    is_assignable_by_admin = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    permissions = Column(Text, nullable=True)  # Comma-separated permission scopes

    # Self-referential relationship for role hierarchy
    parent_role = relationship("Role", remote_side="Role.id", backref="child_roles")
    group = relationship("RoleGroup", backref="roles")

    # Relationships
    user_roles = relationship("UserRole", back_populates="role")
    festival_roles = relationship("FestivalRole", back_populates="role")
    group_memberships = relationship("RoleGroupMembership", back_populates="role")
    dependencies = relationship(
        "RoleDependency", foreign_keys="RoleDependency.role_id", back_populates="role", cascade="all, delete-orphan"
    )
    depended_by = relationship(
        "RoleDependency", foreign_keys="RoleDependency.depends_on_role_id", back_populates="depends_on_role"
    )
    conflicts = relationship(
        "RoleConflict", foreign_keys="RoleConflict.role_id", back_populates="role", cascade="all, delete-orphan"
    )
    conflicted_by = relationship(
        "RoleConflict", foreign_keys="RoleConflict.conflicts_with_role_id", back_populates="conflicts_with_role"
    )

    def __repr__(self):
        return f"<Role(name='{self.name}', scope='{self.scope.value}', level={self.hierarchy_level})>"


class FestivalRole(BaseModel):
    """Festival-specific role assignment linking Role to Festival.

    This allows customizing which roles exist in each festival and their
    specific configuration per festival.
    """

    __tablename__ = "festival_roles"

    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    custom_permissions = Column(Text, nullable=True)  # Override global permissions for this festival
    max_assignees = Column(Integer, nullable=True)  # Limit number of people with this role

    # Relationships
    festival = relationship("Festival", back_populates="festival_roles")
    role = relationship("Role", back_populates="festival_roles")

    def __repr__(self):
        return f"<FestivalRole(festival_id={self.festival_id}, role_id={self.role_id})>"


class RoleDependency(BaseModel):
    """Prerequisite relationship between roles (role X requires role Y)."""

    __tablename__ = "role_dependencies"

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    depends_on_role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    dependency_type = Column(String(20), default="required")  # required, recommended
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True)  # Null = applies globally
    notes = Column(Text, nullable=True)

    role = relationship("Role", foreign_keys=[role_id], back_populates="dependencies")
    depends_on_role = relationship("Role", foreign_keys=[depends_on_role_id], back_populates="depended_by")
    festival = relationship("Festival", backref="role_dependencies")

    def __repr__(self):
        return (
            f"<RoleDependency(role={self.role_id} depends_on {self.depends_on_role_id}, type='{self.dependency_type}')>"
        )


class RoleConflict(BaseModel):
    """Incompatibility between roles (role X conflicts with role Y)."""

    __tablename__ = "role_conflicts"

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    conflicts_with_role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    conflict_type = Column(String(20), default="exclusive")  # exclusive, restricted
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=True)  # Null = applies globally
    notes = Column(Text, nullable=True)

    role = relationship("Role", foreign_keys=[role_id], back_populates="conflicts")
    conflicts_with_role = relationship("Role", foreign_keys=[conflicts_with_role_id], back_populates="conflicted_by")
    festival = relationship("Festival", backref="role_conflicts")

    def __repr__(self):
        return (
            f"<RoleConflict(role={self.role_id} conflicts_with "
            f"{self.conflicts_with_role_id}, type='{self.conflict_type}')>"
        )
