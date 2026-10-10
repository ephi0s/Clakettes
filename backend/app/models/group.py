from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, func, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Group(BaseModel):
    __tablename__ = "groups"
    __table_args__ = (CheckConstraint("max_members IS NULL OR max_members > 0", name="ck_group_max_members"),)

    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    max_members = Column(Integer, nullable=True, default=50)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)

    creator = relationship("User", foreign_keys=[created_by])
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")


class GroupMember(BaseModel):
    __tablename__ = "group_members"
    __table_args__ = (CheckConstraint("role IN ('admin', 'moderator', 'member')", name="ck_group_member_role"),)

    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False, default="member")
    joined_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)

    group = relationship("Group", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
