"""Channel CRUD and membership router for community rooms and private groups."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.database import get_db
from app.models.channel import Channel
from app.models.user import User as UserModel
from app.schemas.channel import (
    ChannelCreate,
    ChannelUpdate,
    ChannelResponse,
    ChannelsPage,
    ChannelMemberCreate,
    ChannelMemberUpdate,
    ChannelMemberResponse,
)
from app.routers.dependencies import get_or_404
from app.routers.permissions import require_channel_admin, require_channel_member
from app.services.channel_service import ChannelService

router = APIRouter()
service = ChannelService()


@router.post("", response_model=ChannelResponse, status_code=201)
async def create_channel(
    data: ChannelCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service.create_channel(db, data, created_by=current_user.id)


@router.get("", response_model=ChannelsPage)
async def list_my_channels(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service.get_channels_for_user(db, current_user.id, page=page, size=size)


@router.get("/public", response_model=ChannelsPage)
async def list_public_channels(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return service.get_public_channels(db, page=page, size=size)


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    channel = get_or_404(db, Channel, channel_id, "Channel")
    if getattr(channel, "channel_type", "public") != "public":
        require_channel_member(db, current_user, channel)
    return channel


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    data: ChannelUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    channel = get_or_404(db, Channel, channel_id, "Channel")
    require_channel_admin(db, current_user, channel)
    return service.update(db, channel_id, data)


@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    channel = get_or_404(db, Channel, channel_id, "Channel")
    require_channel_admin(db, current_user, channel)
    result = service.soft_delete(db, channel_id)
    if not result:
        raise HTTPException(status_code=404, detail="Channel not found")
    return {"message": "Channel deactivated"}


# -- Membership ----------------------------------------------------------------


@router.post("/{channel_id}/members", response_model=ChannelMemberResponse, status_code=201)
async def add_member(
    channel_id: int,
    data: ChannelMemberCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    channel = get_or_404(db, Channel, channel_id, "Channel")
    require_channel_admin(db, current_user, channel)
    return service.add_member(db, channel_id, data.user_id, role=data.role)


@router.get("/{channel_id}/members", response_model=list[ChannelMemberResponse])
async def list_members(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    channel = get_or_404(db, Channel, channel_id, "Channel")
    require_channel_member(db, current_user, channel)
    return service.get_members(db, channel_id)


@router.put("/{channel_id}/members/{user_id}/role", response_model=ChannelMemberResponse)
async def update_member_role(
    channel_id: int,
    user_id: int,
    data: ChannelMemberUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    channel = get_or_404(db, Channel, channel_id, "Channel")
    require_channel_admin(db, current_user, channel)
    return service.update_member_role(db, channel_id, user_id, data.role or "member")


@router.delete("/{channel_id}/members/{user_id}")
async def remove_member(
    channel_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    channel = get_or_404(db, Channel, channel_id, "Channel")
    require_channel_admin(db, current_user, channel)
    service.remove_member(db, channel_id, user_id)
    return {"message": "Member removed"}
