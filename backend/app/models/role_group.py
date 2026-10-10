"""RoleGroup — role categorization into groups (direction, technical, creative, etc.)."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class RoleGroup(BaseModel):
    """Group/category for roles (e.g., 'Dirección', 'Técnica', 'Creativa', 'Hospitality')."""

    __tablename__ = "role_groups"

    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    memberships = relationship("RoleGroupMembership", back_populates="group")

    def __repr__(self):
        return f"<RoleGroup(name='{self.name}')>"


class RoleGroupMembership(BaseModel):
    """Links a role to a group with level and leader flag."""

    __tablename__ = "role_group_memberships"

    group_id = Column(Integer, ForeignKey("role_groups.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    level = Column(Integer, default=0)  # Hierarchy within group (higher = senior)
    is_leader = Column(Boolean, default=False)  # Leader/head of this group
    is_active = Column(Boolean, default=True)

    group = relationship("RoleGroup", back_populates="memberships")
    role = relationship("Role", back_populates="group_memberships")

    def __repr__(self):
        return f"<RoleGroupMembership(group_id={self.group_id}, role_id={self.role_id}, level={self.level})>"
