"""Role-based permission helpers for the Clakettes API.

Permission rules (checked in order):
1. Granular UserRole/Role tables (primary)
2. Legacy ``user.role`` field fallback

Permission levels by role name:
- admin:      can edit/delete any entity
- organizer:  can edit own profile + festivals they organize + users in their festivals
- user:       can edit own profile + own short films
- jury:       can edit own profile only

Deletion: only admin and organizer can delete user profiles.
"""

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.role import Role, RoleScope
from app.models.user import User
from app.models.shortfilm import ShortFilm
from app.models.channel import ChannelMember
from app.models.festival import Festival
from app.models.user_festival import user_festival
from app.models.user_role import UserRole, UserRoleStatus

# ---------------------------------------------------------------------------
# Granular role helpers (UserRole + Role tables)
# ---------------------------------------------------------------------------


def _has_active_role(
    db: Session,
    user_id: int,
    role_name: str,
    festival_id: int | None = None,
) -> bool:
    """Return True if *user_id* has an active/approved *role_name*.

    Checks the granular ``UserRole`` + ``Role`` tables.  When *festival_id*
    is given, both festival-scoped and global roles are considered.
    """
    query = (
        db.query(UserRole)
        .join(Role, UserRole.role_id == Role.id)
        .filter(
            UserRole.user_id == user_id,
            Role.name == role_name,
            UserRole.status.in_([UserRoleStatus.ACTIVE, UserRoleStatus.APPROVED]),
        )
    )
    if festival_id is not None:
        query = query.filter((UserRole.festival_id == festival_id) | (UserRole.festival_id.is_(None)))
    return query.first() is not None


def _has_any_global_role(
    db: Session,
    user_id: int,
    role_names: list[str],
) -> bool:
    """Return True if *user_id* has any of *role_names* as a global role."""
    return (
        db.query(UserRole)
        .join(Role, UserRole.role_id == Role.id)
        .filter(
            UserRole.user_id == user_id,
            Role.name.in_(role_names),
            Role.scope == RoleScope.GLOBAL,
            UserRole.status.in_([UserRoleStatus.ACTIVE, UserRoleStatus.APPROVED]),
        )
        .first()
        is not None
    )


def _get_highest_role_level(
    db: Session,
    user_id: int,
    festival_id: int | None = None,
) -> int:
    """Return the highest hierarchy level among the user's active roles.

    0 is returned when no roles are found.
    """
    query = (
        db.query(func.max(Role.hierarchy_level))
        .select_from(UserRole)
        .join(Role, UserRole.role_id == Role.id)
        .filter(
            UserRole.user_id == user_id,
            UserRole.status.in_([UserRoleStatus.ACTIVE, UserRoleStatus.APPROVED]),
        )
    )
    if festival_id is not None:
        query = query.filter((UserRole.festival_id == festival_id) | (UserRole.festival_id.is_(None)))
    return query.scalar() or 0


# ---------------------------------------------------------------------------
# Legacy helpers (user.role column — kept for backwards compatibility)
# ---------------------------------------------------------------------------


def _has_legacy_role(user: User, role_name: str) -> bool:
    """Check the legacy ``user.role`` column."""
    return (user.role or "").lower() == role_name.lower()


# ---------------------------------------------------------------------------
# Permission check helpers (granular first, then legacy fallback)
# ---------------------------------------------------------------------------


def _is_admin(db: Session, user: User) -> bool:
    """Return True if *user* has admin-level permissions."""
    return _has_active_role(db, user.id, "admin") or _has_legacy_role(user, "admin")


def _is_organizer(db: Session, user: User) -> bool:
    """Return True if *user* has organizer-level permissions."""
    return _has_active_role(db, user.id, "organizer") or _has_legacy_role(user, "organizer")


def _is_organizer_of_festival(
    db: Session,
    user_id: int,
    festival_id: int,
) -> bool:
    """Check the legacy ``user_festival`` table."""
    row = db.execute(
        select(user_festival).where(
            user_festival.c.user_id == user_id,
            user_festival.c.festival_id == festival_id,
            user_festival.c.role == "organizer",
        )
    ).first()
    if row:
        return True
    # Also check the granular system
    return _has_active_role(db, user_id, "organizer", festival_id=festival_id)


def _is_user_in_organizer_festivals(
    db: Session,
    organizer_id: int,
    target_user_id: int,
) -> bool:
    """Check if *target_user* belongs to any festival where *organizer* has rights."""
    org_festivals = (
        db.execute(
            select(user_festival.c.festival_id).where(
                user_festival.c.user_id == organizer_id,
                user_festival.c.role == "organizer",
            )
        )
        .scalars()
        .all()
    )
    if not org_festivals:
        # Also check granular system for any festival roles
        uroles = (
            db.query(UserRole)
            .join(Role, UserRole.role_id == Role.id)
            .filter(
                UserRole.user_id == organizer_id,
                UserRole.status.in_([UserRoleStatus.ACTIVE, UserRoleStatus.APPROVED]),
                UserRole.festival_id.isnot(None),
            )
            .all()
        )
        org_festivals = [ur.festival_id for ur in uroles if ur.festival_id]
    if not org_festivals:
        return False
    member = db.execute(
        select(user_festival).where(
            user_festival.c.user_id == target_user_id,
            user_festival.c.festival_id.in_(org_festivals),
        )
    ).first()
    return member is not None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_admin(user: User) -> bool:
    """Return True if *user* is an admin (checks legacy role + granular UserRole).

    Uses the already-loaded ``user.user_roles`` relationship (no extra DB query).
    """
    if user.role == "admin":
        return True
    for ur in user.user_roles:
        if ur.role and ur.role.name == "admin" and ur.status == UserRoleStatus.APPROVED.value:
            return True
    return False


def can_edit_user(db: Session, editor: User, target_user: User) -> bool:
    """Return True if *editor* is allowed to modify *target_user*'s profile."""
    if _is_admin(db, editor):
        return True
    if editor.id == target_user.id:
        return True
    if _is_organizer(db, editor):
        return _is_user_in_organizer_festivals(db, editor.id, target_user.id)
    return False


def can_delete_user(db: Session, deleter: User, target_user: User) -> bool:
    """Return True if *deleter* can delete *target_user*."""
    if _is_admin(db, deleter):
        return True
    if _is_organizer(db, deleter):
        return _is_user_in_organizer_festivals(db, deleter.id, target_user.id)
    return False


def can_edit_festival(db: Session, editor: User, festival: Festival) -> bool:
    """Return True if *editor* can modify *festival*."""
    if _is_admin(db, editor):
        return True
    if _is_organizer(db, editor):
        return _is_organizer_of_festival(db, editor.id, festival.id)
    return False


def can_delete_festival(db: Session, deleter: User, festival: Festival) -> bool:
    """Return True if *deleter* can delete *festival*."""
    if _is_admin(db, deleter):
        return True
    if _is_organizer(db, deleter):
        return _is_organizer_of_festival(db, deleter.id, festival.id)
    return False


def can_edit_shortfilm(db: Session, editor: User, shortfilm: ShortFilm) -> bool:
    """Return True if *editor* can modify *shortfilm*."""
    if _is_admin(db, editor):
        return True
    if editor.id == shortfilm.user_id:
        return True
    return False


def can_delete_shortfilm(db: Session, deleter: User, shortfilm: ShortFilm) -> bool:
    """Return True if *deleter* can delete *shortfilm*."""
    if _is_admin(db, deleter):
        return True
    if deleter.id == shortfilm.user_id:
        return True
    return False


# ---------------------------------------------------------------------------
# Reusable FastAPI dependencies / guards
# ---------------------------------------------------------------------------


def require_admin(user: User) -> None:
    """Raise 403 unless *user* is a global admin."""
    if not is_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")


def can_manage_festival(db: Session, user: User, festival_id: int | None) -> bool:
    """Return True if *user* is a global admin or an organizer of *festival_id*."""
    if is_admin(user):
        return True
    if festival_id is None:
        return False
    return _is_organizer_of_festival(db, user.id, festival_id)


def require_festival_admin(db: Session, user: User, festival_id: int | None) -> None:
    """Raise 403 unless *user* can manage the festival identified by *festival_id*."""
    if not can_manage_festival(db, user, festival_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


def can_manage_role_scope(db: Session, user: User, festival_id: int | None) -> bool:
    """Return True if *user* can assign roles in the given scope.

    ``None`` means a global role: only global admins can manage it.
    """
    if festival_id is None:
        return is_admin(user)
    return can_manage_festival(db, user, festival_id)


def require_role_scope_admin(db: Session, user: User, festival_id: int | None) -> None:
    """Raise 403 unless *user* can assign roles in the given scope."""
    if not can_manage_role_scope(db, user, festival_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


def can_manage_form(db: Session, user: User, form) -> bool:
    """Return True if *user* is the form creator, a global admin, or an organizer of its festival."""
    if is_admin(user):
        return True
    if form.created_by and form.created_by == user.id:
        return True
    if form.festival_id:
        return _is_organizer_of_festival(db, user.id, form.festival_id)
    return False


def require_form_admin(db: Session, user: User, form) -> None:
    """Raise 403 unless *user* can manage the given form."""
    if not can_manage_form(db, user, form):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


def can_manage_channel(db: Session, user: User, channel) -> bool:
    """Return True if *user* is a global admin, the channel creator, or an admin member."""
    if is_admin(user):
        return True
    if channel.created_by == user.id:
        return True
    membership = (
        db.query(ChannelMember)
        .filter(
            ChannelMember.channel_id == channel.id,
            ChannelMember.user_id == user.id,
            ChannelMember.role == "admin",
            ChannelMember.is_active.is_(True),
        )
        .first()
    )
    return membership is not None


def require_channel_admin(db: Session, user: User, channel) -> None:
    """Raise 403 unless *user* can manage the given channel."""
    if not can_manage_channel(db, user, channel):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


def is_channel_member(db: Session, user_id: int, channel) -> bool:
    """Return True if *user_id* is an active member of the channel."""
    return (
        db.query(ChannelMember)
        .filter(
            ChannelMember.channel_id == channel.id,
            ChannelMember.user_id == user_id,
            ChannelMember.is_active.is_(True),
        )
        .first()
        is not None
    )


def require_channel_member(db: Session, user: User, channel) -> None:
    """Raise 403 unless *user* is a member, the creator, or a global admin."""
    if is_admin(user):
        return
    if channel.created_by == user.id:
        return
    if is_channel_member(db, user.id, channel):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this channel")


def require_location_admin(db: Session, user: User, location) -> None:
    """Raise 403 unless *user* is a global admin or the location's creator."""
    if is_admin(user) or location.added_by == user.id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
