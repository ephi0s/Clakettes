from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from app.models.group import Group, GroupMember
from app.models.role_group import RoleGroup, RoleGroupMembership
from app.models.committee import Committee, CommitteeMember
from app.models.role_delegation import RoleDelegation
from app.models.role_transition import RoleTransition
from app.schemas.group import GroupCreate, GroupUpdate
from app.schemas.role_group import (
    RoleGroupCreate,
    RoleGroupUpdate,
    RoleGroupMembershipCreate,
    RoleGroupMembershipUpdate,
)
from app.schemas.committee import (
    CommitteeCreate,
    CommitteeUpdate,
    CommitteeMemberCreate,
    CommitteeMemberUpdate,
)
from app.schemas.role_delegation import RoleDelegationCreate, RoleDelegationUpdate
from app.schemas.role_transition import RoleTransitionCreate
from app.enums import DelegationStatus
from datetime import datetime, timezone
from .base_service import BaseService


class GroupService(BaseService[Group, GroupCreate, GroupUpdate]):
    def __init__(self):
        super().__init__(Group)

    def create_group(self, db: Session, obj_in: GroupCreate, created_by: int) -> Group:
        group = Group(
            name=obj_in.name,
            description=obj_in.description,
            max_members=obj_in.max_members or 50,
            created_by=created_by,
        )
        db.add(group)
        db.flush()

        member = GroupMember(
            group_id=group.id,
            user_id=created_by,
            role="admin",
        )
        db.add(member)
        db.commit()
        db.refresh(group)
        return group

    def get_groups_for_user(self, db: Session, user_id: int, page: int = 1, size: int = 20):
        query = (
            db.query(Group)
            .join(GroupMember)
            .filter(
                GroupMember.user_id == user_id,
                GroupMember.is_active,
                Group.is_active,
            )
            .order_by(Group.created_at.desc())
        )
        return self.paginate(query, page, size)

    def get_member_count(self, db: Session, group_id: int) -> int:
        return (
            db.query(func.count(GroupMember.id))
            .filter(
                GroupMember.group_id == group_id,
                GroupMember.is_active,
            )
            .scalar()
            or 0
        )

    def add_member(self, db: Session, group_id: int, user_id: int, role: str = "member") -> GroupMember:
        group = self.get(db, group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        existing = (
            db.query(GroupMember)
            .filter(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
            )
            .first()
        )
        if existing:
            if existing.is_active:
                raise HTTPException(status_code=400, detail="User is already a member")
            existing.is_active = True
            existing.role = role
            db.commit()
            db.refresh(existing)
            return existing

        if group.max_members is not None:
            count = self.get_member_count(db, group_id)
            if count >= group.max_members:
                raise HTTPException(
                    status_code=400,
                    detail=f"Group is full (max {group.max_members} members)",
                )

        member = GroupMember(
            group_id=group_id,
            user_id=user_id,
            role=role,
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    def remove_member(self, db: Session, group_id: int, user_id: int) -> None:
        member = (
            db.query(GroupMember)
            .filter(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
                GroupMember.is_active,
            )
            .first()
        )
        if not member:
            raise HTTPException(status_code=404, detail="Membership not found")
        member.is_active = False
        db.commit()

    def get_members(self, db: Session, group_id: int) -> list[GroupMember]:
        return (
            db.query(GroupMember)
            .filter(
                GroupMember.group_id == group_id,
                GroupMember.is_active,
            )
            .all()
        )

    def soft_delete(self, db: Session, group_id: int) -> Group | None:
        group = self.get(db, group_id)
        if not group:
            return None
        group.is_active = False
        db.commit()
        db.refresh(group)
        return group

    def get_member_role(self, db: Session, group_id: int, user_id: int) -> str | None:
        member = (
            db.query(GroupMember)
            .filter(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
                GroupMember.is_active,
            )
            .first()
        )
        return member.role if member else None

    def update_member_role(self, db: Session, group_id: int, user_id: int, role: str) -> GroupMember:
        member = (
            db.query(GroupMember)
            .filter(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
                GroupMember.is_active,
            )
            .first()
        )
        if not member:
            raise HTTPException(status_code=404, detail="Membership not found")
        member.role = role
        db.commit()
        db.refresh(member)
        return member


class RoleGroupService(BaseService[RoleGroup, RoleGroupCreate, RoleGroupUpdate]):
    def __init__(self):
        super().__init__(RoleGroup)

    def get_by_name(self, db: Session, name: str) -> RoleGroup | None:
        return db.query(RoleGroup).filter(RoleGroup.name == name).first()

    def get_active(self, db: Session) -> list[RoleGroup]:
        return db.query(RoleGroup).filter(RoleGroup.is_active).order_by(RoleGroup.sort_order).all()

    def get_all_paginated(self, db: Session, page: int, size: int, is_active: bool | None = None):
        query = db.query(RoleGroup)
        if is_active is not None:
            query = query.filter(RoleGroup.is_active == is_active)
        query = query.order_by(RoleGroup.sort_order)
        return self.paginate(query, page, size)


class RoleGroupMembershipService(
    BaseService[RoleGroupMembership, RoleGroupMembershipCreate, RoleGroupMembershipUpdate]
):
    def __init__(self):
        super().__init__(RoleGroupMembership)

    def get_by_group(self, db: Session, group_id: int) -> list[RoleGroupMembership]:
        return (
            db.query(RoleGroupMembership)
            .filter(RoleGroupMembership.group_id == group_id, RoleGroupMembership.is_active)
            .order_by(RoleGroupMembership.level.desc())
            .all()
        )

    def get_leaders(self, db: Session, group_id: int) -> list[RoleGroupMembership]:
        return (
            db.query(RoleGroupMembership)
            .filter(
                RoleGroupMembership.group_id == group_id,
                RoleGroupMembership.is_active,
                RoleGroupMembership.is_leader,
            )
            .all()
        )

    def get_by_group_paginated(self, db: Session, group_id: int, page: int, size: int):
        query = (
            db.query(RoleGroupMembership)
            .filter(RoleGroupMembership.group_id == group_id, RoleGroupMembership.is_active)
            .order_by(RoleGroupMembership.level.desc())
        )
        return self.paginate(query, page, size)


class CommitteeService(BaseService[Committee, CommitteeCreate, CommitteeUpdate]):
    def __init__(self):
        super().__init__(Committee)

    def get_by_festival(self, db: Session, festival_id: int) -> list[Committee]:
        return (
            db.query(Committee)
            .filter(Committee.festival_id == festival_id, Committee.is_active)
            .order_by(Committee.name)
            .all()
        )

    def get_by_festival_paginated(self, db: Session, festival_id: int, page: int, size: int):
        query = (
            db.query(Committee)
            .filter(Committee.festival_id == festival_id, Committee.is_active)
            .order_by(Committee.name)
        )
        return self.paginate(query, page, size)

    def get_member_count(self, db: Session, committee_id: int) -> int:
        return (
            db.query(func.count(CommitteeMember.id))
            .filter(CommitteeMember.committee_id == committee_id, CommitteeMember.is_active)
            .scalar()
            or 0
        )

    def get_member_counts(self, db: Session, committee_ids: list[int]) -> dict[int, int]:
        if not committee_ids:
            return {}
        rows = (
            db.query(CommitteeMember.committee_id, func.count(CommitteeMember.id))
            .filter(CommitteeMember.committee_id.in_(committee_ids), CommitteeMember.is_active)
            .group_by(CommitteeMember.committee_id)
            .all()
        )
        return {committee_id: count for committee_id, count in rows}


class CommitteeMemberService(BaseService[CommitteeMember, CommitteeMemberCreate, CommitteeMemberUpdate]):
    def __init__(self):
        super().__init__(CommitteeMember)

    def get_by_committee(self, db: Session, committee_id: int) -> list[CommitteeMember]:
        return (
            db.query(CommitteeMember)
            .filter(CommitteeMember.committee_id == committee_id, CommitteeMember.is_active)
            .all()
        )

    def get_by_committee_paginated(self, db: Session, committee_id: int, page: int, size: int):
        query = (
            db.query(CommitteeMember)
            .filter(CommitteeMember.committee_id == committee_id, CommitteeMember.is_active)
            .order_by(CommitteeMember.role_in_committee)
        )
        return self.paginate(query, page, size)

    def get_membership(self, db: Session, committee_id: int, user_id: int) -> CommitteeMember | None:
        return (
            db.query(CommitteeMember)
            .filter(
                CommitteeMember.committee_id == committee_id,
                CommitteeMember.user_id == user_id,
                CommitteeMember.is_active,
            )
            .first()
        )


class RoleDelegationService(BaseService[RoleDelegation, RoleDelegationCreate, RoleDelegationUpdate]):
    def __init__(self):
        super().__init__(RoleDelegation)

    def get_all_paginated(
        self,
        db: Session,
        page: int,
        size: int,
        delegator_id: int | None = None,
        delegate_id: int | None = None,
        status: str | None = None,
    ):
        query = db.query(RoleDelegation)
        if delegator_id is not None:
            query = query.filter(RoleDelegation.delegator_id == delegator_id)
        if delegate_id is not None:
            query = query.filter(RoleDelegation.delegate_id == delegate_id)
        if status is not None:
            query = query.filter(RoleDelegation.status == status)
        query = query.order_by(RoleDelegation.created_at.desc())
        return self.paginate(query, page, size)

    def revoke(
        self,
        db: Session,
        delegation_id: int,
        revoked_by: int,
        reason: str | None = None,
    ) -> RoleDelegation | None:
        delegation = self.get(db, delegation_id)
        if not delegation:
            return None
        delegation.status = DelegationStatus.REVOKED.value
        delegation.revoked_by = revoked_by
        delegation.revoked_at = datetime.now(timezone.utc)
        delegation.revoked_reason = reason
        db.commit()
        db.refresh(delegation)
        return delegation

    def get_active_by_delegate(self, db: Session, user_id: int) -> list[RoleDelegation]:
        return (
            db.query(RoleDelegation)
            .filter(
                RoleDelegation.delegate_id == user_id,
                RoleDelegation.status == DelegationStatus.ACTIVE.value,
            )
            .all()
        )

    def get_active_by_delegator(self, db: Session, user_id: int) -> list[RoleDelegation]:
        return (
            db.query(RoleDelegation)
            .filter(
                RoleDelegation.delegator_id == user_id,
                RoleDelegation.status == DelegationStatus.ACTIVE.value,
            )
            .all()
        )


class RoleTransitionService(BaseService[RoleTransition, RoleTransitionCreate, None]):
    def __init__(self):
        super().__init__(RoleTransition)

    def record_transition(
        self,
        db: Session,
        *,
        user_id: int,
        to_role_id: int,
        transition_type: str,
        changed_by: int,
        from_role_id: int | None = None,
        from_festival_id: int | None = None,
        to_festival_id: int | None = None,
        reason: str | None = None,
    ) -> RoleTransition:
        obj = RoleTransition(
            user_id=user_id,
            to_role_id=to_role_id,
            from_role_id=from_role_id,
            transition_type=transition_type,
            changed_by=changed_by,
            from_festival_id=from_festival_id,
            to_festival_id=to_festival_id,
            reason=reason,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get_by_user(self, db: Session, user_id: int) -> list[RoleTransition]:
        return (
            db.query(RoleTransition)
            .filter(RoleTransition.user_id == user_id)
            .order_by(RoleTransition.transitioned_at.desc())
            .all()
        )

    def get_by_festival(self, db: Session, festival_id: int) -> list[RoleTransition]:
        return (
            db.query(RoleTransition)
            .filter((RoleTransition.from_festival_id == festival_id) | (RoleTransition.to_festival_id == festival_id))
            .order_by(RoleTransition.transitioned_at.desc())
            .all()
        )

    def get_all_paginated(
        self,
        db: Session,
        page: int,
        size: int,
        user_id: int | None = None,
        transition_type: str | None = None,
    ):
        query = db.query(RoleTransition)
        if user_id is not None:
            query = query.filter(RoleTransition.user_id == user_id)
        if transition_type is not None:
            query = query.filter(RoleTransition.transition_type == transition_type)
        query = query.order_by(RoleTransition.transitioned_at.desc())
        return self.paginate(query, page, size)
