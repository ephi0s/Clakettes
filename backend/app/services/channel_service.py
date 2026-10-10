from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from app.models.channel import Channel, ChannelMember
from app.schemas.channel import ChannelCreate, ChannelUpdate
from .base_service import BaseService


class ChannelService(BaseService[Channel, ChannelCreate, ChannelUpdate]):
    """CRUD + membership management for chat channels and private rooms."""

    def __init__(self):
        super().__init__(Channel)

    # -- Channel CRUD -----------------------------------------------------------

    def create_channel(self, db: Session, obj_in: ChannelCreate, created_by: int) -> Channel:
        """Create a channel and auto-add the creator as admin."""
        channel = Channel(
            name=obj_in.name,
            description=obj_in.description,
            channel_type=obj_in.channel_type,
            max_members=obj_in.max_members or (20 if obj_in.channel_type == "private" else None),
            created_by=created_by,
        )
        db.add(channel)
        db.flush()

        # Creator is automatically admin
        member = ChannelMember(
            channel_id=channel.id,
            user_id=created_by,
            role="admin",
        )
        db.add(member)
        db.commit()
        db.refresh(channel)
        return channel

    def get_channels_for_user(self, db: Session, user_id: int, page: int = 1, size: int = 20):
        """List channels the user is a member of."""
        query = (
            db.query(Channel)
            .join(ChannelMember)
            .filter(
                ChannelMember.user_id == user_id,
                ChannelMember.is_active,
                Channel.is_active,
            )
            .order_by(Channel.created_at.desc())
        )
        return self.paginate(query, page, size)

    def get_public_channels(self, db: Session, page: int = 1, size: int = 20):
        """List all active community channels."""
        query = (
            db.query(Channel)
            .filter(
                Channel.channel_type == "community",
                Channel.is_active,
            )
            .order_by(Channel.created_at.desc())
        )
        return self.paginate(query, page, size)

    def get_member_count(self, db: Session, channel_id: int) -> int:
        """Return the number of active members in a channel."""
        return (
            db.query(func.count(ChannelMember.id))
            .filter(
                ChannelMember.channel_id == channel_id,
                ChannelMember.is_active,
            )
            .scalar()
            or 0
        )

    # -- Membership -------------------------------------------------------------

    def add_member(self, db: Session, channel_id: int, user_id: int, role: str = "member") -> ChannelMember:
        """Add a user to a channel. Raises 400 if channel is full (private rooms)."""
        channel = self.get(db, channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")

        # Check if already a member
        existing = (
            db.query(ChannelMember)
            .filter(
                ChannelMember.channel_id == channel_id,
                ChannelMember.user_id == user_id,
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

        # Enforce max_members for private rooms
        if channel.max_members is not None:
            count = self.get_member_count(db, channel_id)
            if count >= channel.max_members:
                raise HTTPException(
                    status_code=400,
                    detail=f"Channel is full (max {channel.max_members} members)",
                )

        member = ChannelMember(
            channel_id=channel_id,
            user_id=user_id,
            role=role,
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    def remove_member(self, db: Session, channel_id: int, user_id: int) -> None:
        """Soft-delete a channel membership."""
        member = (
            db.query(ChannelMember)
            .filter(
                ChannelMember.channel_id == channel_id,
                ChannelMember.user_id == user_id,
                ChannelMember.is_active,
            )
            .first()
        )
        if not member:
            raise HTTPException(status_code=404, detail="Membership not found")
        member.is_active = False
        db.commit()

    def get_members(self, db: Session, channel_id: int) -> list[ChannelMember]:
        """List active members of a channel."""
        return (
            db.query(ChannelMember)
            .filter(
                ChannelMember.channel_id == channel_id,
                ChannelMember.is_active,
            )
            .all()
        )

    def soft_delete(self, db: Session, channel_id: int) -> Channel | None:
        channel = self.get(db, channel_id)
        if not channel:
            return None
        channel.is_active = False
        db.commit()
        db.refresh(channel)
        return channel

    def get_member_role(self, db: Session, channel_id: int, user_id: int) -> str | None:
        """Return the role of a user in a channel, or None if not a member."""
        member = (
            db.query(ChannelMember)
            .filter(
                ChannelMember.channel_id == channel_id,
                ChannelMember.user_id == user_id,
                ChannelMember.is_active,
            )
            .first()
        )
        return member.role if member else None

    def update_member_role(self, db: Session, channel_id: int, user_id: int, role: str) -> ChannelMember:
        """Change a member's role."""
        member = (
            db.query(ChannelMember)
            .filter(
                ChannelMember.channel_id == channel_id,
                ChannelMember.user_id == user_id,
                ChannelMember.is_active,
            )
            .first()
        )
        if not member:
            raise HTTPException(status_code=404, detail="Membership not found")
        member.role = role
        db.commit()
        db.refresh(member)
        return member
