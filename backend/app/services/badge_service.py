from sqlalchemy.orm import Session
from app.enums import UserRoleStatus
from app.models.award import Award
from app.models.badge import Badge, BadgeAssignment
from app.models.role import Role
from app.models.user_festival import user_festival
from app.models.user_role import UserRole
from app.schemas.badge import BadgeCreate, BadgeUpdate
from .base_service import BaseService

ACTIVE_STATUSES = {UserRoleStatus.ACTIVE.value, UserRoleStatus.APPROVED.value}


class BadgeService(BaseService[Badge, BadgeCreate, BadgeUpdate]):
    def __init__(self):
        super().__init__(Badge)

    def list_active(self, db: Session, page: int = 1, size: int = 20, scope: str | None = None):
        filters = [Badge.is_active.is_(True)]
        if scope:
            filters.append(Badge.scope == scope)
        query = db.query(Badge).filter(*filters).order_by(Badge.id.desc())
        return self.paginate(query, page, size)

    def list_assignments_for_user(self, db: Session, user_id: int, page: int = 1, size: int = 50):
        query = (
            db.query(BadgeAssignment)
            .filter(BadgeAssignment.target_user_id == user_id)
            .order_by(BadgeAssignment.id.desc())
        )
        return self.paginate(query, page, size)

    def list_assignments_for_festival(self, db: Session, festival_id: int, page: int = 1, size: int = 50):
        query = (
            db.query(BadgeAssignment)
            .filter(BadgeAssignment.target_festival_id == festival_id)
            .order_by(BadgeAssignment.id.desc())
        )
        return self.paginate(query, page, size)

    def grant(
        self,
        db: Session,
        badge: Badge,
        granted_by: int,
        target_user_id: int | None = None,
        target_festival_id: int | None = None,
        grant_festival_id: int | None = None,
        reason: str | None = None,
    ) -> BadgeAssignment:
        assignment = BadgeAssignment(
            badge_id=badge.id,
            target_user_id=target_user_id,
            target_festival_id=target_festival_id,
            granted_by=granted_by,
            grant_festival_id=grant_festival_id,
            reason=reason,
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment


def _festival_count(db: Session, user_id: int) -> int:
    return db.query(user_festival).filter(user_festival.c.user_id == user_id).count()


def _has_legacy_role(db: Session, user_id: int, role: str, festival_id: int | None = None) -> bool:
    query = db.query(user_festival).filter(user_festival.c.user_id == user_id, user_festival.c.role == role.lower())
    if festival_id is not None:
        query = query.filter(user_festival.c.festival_id == festival_id)
    return query.first() is not None


def _has_granular_role(db: Session, user_id: int, role: str, festival_id: int | None = None) -> bool:
    query = (
        db.query(UserRole)
        .join(Role, UserRole.role_id == Role.id)
        .filter(
            UserRole.user_id == user_id,
            Role.name == role.lower(),
            UserRole.status.in_(ACTIVE_STATUSES),
        )
    )
    if festival_id is not None:
        query = query.filter((UserRole.festival_id == festival_id) | (UserRole.festival_id.is_(None)))
    return query.first() is not None


def check_eligibility(db: Session, badge: Badge, user_id: int) -> tuple[bool, str]:
    """Evaluate a badge's JSON conditions for a user.

    Supported descriptors: ``{"type": "manual"}`` (always eligible, granted at
    someone's discretion), ``{"type": "veteran", "min_festivals": N}``,
    ``{"type": "role", "role": "<name>", "festival_id": <optional>}``,
    ``{"type": "award", "festival_id": <optional>}``. Unknown types are not
    auto-approved and require an admin override.
    """
    conditions = badge.conditions or {"type": "manual"}
    ctype = conditions.get("type", "manual")
    if ctype == "manual":
        return True, "Manual grant"
    if ctype == "veteran":
        minimum = int(conditions.get("min_festivals", 1))
        count = _festival_count(db, user_id)
        if count >= minimum:
            return True, f"Member of {count} festivals"
        return False, f"Requires {minimum} festivals, has {count}"
    if ctype == "role":
        role = str(conditions.get("role", "")).lower()
        festival_id = conditions.get("festival_id") or badge.festival_id
        if _has_legacy_role(db, user_id, role, festival_id) or _has_granular_role(db, user_id, role, festival_id):
            return True, f"Holds role {role}"
        return False, f"Missing role {role}"
    if ctype == "award":
        festival_id = conditions.get("festival_id") or badge.festival_id
        query = db.query(Award).filter(Award.user_id == user_id)
        if festival_id is not None:
            query = query.filter(Award.festival_id == festival_id)
        if query.first() is not None:
            return True, "Award holder"
        return False, "No award found"
    return False, f"Unknown condition type {ctype}"
