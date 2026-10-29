"""Chat REST + WebSocket router with channel and E2EE support."""

import logging

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user, validate_access_token
from app.chat_backend.registry import chat_backend_registry
from app.database import get_db
from app.models.user import User as UserModel
from app.schemas.message import MessageCreate, MessageResponse, MessagesPage
from app.services.message_service import MessageService
from app.services.user_service import UserService
from app.services.channel_service import ChannelService
from app.services.group_service import GroupService
from app.schemas.group import GroupCreate, GroupResponse, GroupsPage, GroupMemberResponse
from app.models.channel import Channel
from app.models.message import Message
from app.routers.dependencies import get_or_404
from app.routers.permissions import is_admin, require_channel_member

logger = logging.getLogger(__name__)

router = APIRouter()
service = MessageService()
user_service = UserService()
channel_service = ChannelService()
group_service = GroupService()

# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------


@router.get("/messages", response_model=MessagesPage)
async def list_messages(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    sender_id: int | None = None,
    receiver_id: int | None = None,
    group_id: int | None = None,
    channel_id: int | None = None,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if channel_id is not None:
        channel = get_or_404(db, Channel, channel_id, "Channel")
        require_channel_member(db, current_user, channel)
    if group_id is not None:
        group = group_service.get(db, group_id)
        if not group or not group.is_active:
            raise HTTPException(status_code=404, detail="Group not found")
        role = group_service.get_member_role(db, group_id, current_user.id)
        if role is None and not is_admin(current_user):
            raise HTTPException(status_code=403, detail="Not a member of this group")
    if group_id is None and channel_id is None:
        if sender_id is not None and receiver_id is not None and current_user.id not in (sender_id, receiver_id):
            raise HTTPException(status_code=403, detail="Not a participant of this conversation")
        if sender_id is not None and sender_id != current_user.id and receiver_id is None:
            receiver_id = current_user.id
        if receiver_id is not None and receiver_id != current_user.id and sender_id is None:
            sender_id = current_user.id
    return service.get_multi_paginated(
        db,
        page=page,
        size=size,
        sender_id=sender_id,
        receiver_id=receiver_id,
        group_id=group_id,
        channel_id=channel_id,
        unread_only=unread_only,
        user_id=current_user.id,
    )


@router.post("/messages", response_model=MessageResponse, status_code=201)
async def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    # Prevent sender_id spoofing — always use the authenticated user's ID
    message.sender_id = current_user.id
    if message.channel_id is not None:
        channel = get_or_404(db, Channel, message.channel_id, "Channel")
        require_channel_member(db, current_user, channel)
        if getattr(channel, "channel_type", None) == "broadcast":
            role = channel_service.get_member_role(db, channel.id, current_user.id)
            if role not in ("admin", "moderator") and not is_admin(current_user):
                raise HTTPException(status_code=403, detail="Only admins can post in broadcast channels")
    db_msg = service.create(db, message)
    backend = chat_backend_registry.backend

    # Broadcast to channel members if this is a channel message.
    if db_msg.channel_id:
        members = channel_service.get_members(db, db_msg.channel_id)
        for member in members:
            if member.user_id != db_msg.sender_id:
                await backend.send_message(
                    message_id=db_msg.id,
                    sender_id=db_msg.sender_id,
                    receiver_id=member.user_id,
                    group_id=None,
                    channel_id=db_msg.channel_id,
                    content=db_msg.content,
                    message_type=db_msg.message_type,
                    media_url=db_msg.media_url,
                    latitude=db_msg.latitude,
                    longitude=db_msg.longitude,
                    vcard_data=db_msg.vcard_data,
                    ical_data=db_msg.ical_data,
                    created_at=db_msg.created_at.isoformat() if db_msg.created_at else None,
                )
    elif db_msg.group_id:
        members = group_service.get_members(db, db_msg.group_id)
        for member in members:
            if member.user_id != db_msg.sender_id:
                await backend.send_message(
                    message_id=db_msg.id,
                    sender_id=db_msg.sender_id,
                    receiver_id=member.user_id,
                    group_id=db_msg.group_id,
                    channel_id=None,
                    content=db_msg.content,
                    message_type=db_msg.message_type,
                    media_url=db_msg.media_url,
                    latitude=db_msg.latitude,
                    longitude=db_msg.longitude,
                    vcard_data=db_msg.vcard_data,
                    ical_data=db_msg.ical_data,
                    created_at=db_msg.created_at.isoformat() if db_msg.created_at else None,
                )
    else:
        await backend.send_message(
            message_id=db_msg.id,
            sender_id=db_msg.sender_id,
            receiver_id=db_msg.receiver_id,
            group_id=db_msg.group_id,
            channel_id=db_msg.channel_id,
            content=db_msg.content,
            message_type=db_msg.message_type,
            media_url=db_msg.media_url,
            latitude=db_msg.latitude,
            longitude=db_msg.longitude,
            vcard_data=db_msg.vcard_data,
            ical_data=db_msg.ical_data,
            created_at=db_msg.created_at.isoformat() if db_msg.created_at else None,
        )

    return db_msg


@router.put("/messages/{message_id}/read")
async def mark_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    message = get_or_404(db, Message, message_id, "Message")
    if not is_admin(current_user) and message.sender_id != current_user.id and message.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not a participant of this conversation")

    service.mark_as_read(db, message_id)

    backend = chat_backend_registry.backend
    if hasattr(backend, "mark_read"):
        await backend.mark_read(message_id, current_user.id)

    return {"message": "Message marked as read"}


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    message = get_or_404(db, Message, message_id, "Message")
    if message.sender_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only the sender can delete this message")
    deleted = service.delete(db, message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Message deleted"}


# ---------------------------------------------------------------------------
# Group endpoints
# ---------------------------------------------------------------------------


@router.get("/groups", response_model=GroupsPage)
async def list_groups(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return group_service.get_groups_for_user(db, current_user.id, page=page, size=size)


@router.post("/groups", response_model=GroupResponse, status_code=201)
async def create_group(
    group: GroupCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return group_service.create_group(db, group, current_user.id)


@router.get("/groups/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    group = group_service.get(db, group_id)
    if not group or not group.is_active:
        raise HTTPException(status_code=404, detail="Group not found")
    role = group_service.get_member_role(db, group_id, current_user.id)
    if role is None and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    group.member_count = group_service.get_member_count(db, group_id)
    return group


@router.delete("/groups/{group_id}", status_code=204)
async def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    role = group_service.get_member_role(db, group_id, current_user.id)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only group admins can delete the group")
    result = group_service.soft_delete(db, group_id)
    if not result:
        raise HTTPException(status_code=404, detail="Group not found")


@router.get("/groups/{group_id}/members", response_model=list[GroupMemberResponse])
async def list_group_members(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    group = group_service.get(db, group_id)
    if not group or not group.is_active:
        raise HTTPException(status_code=404, detail="Group not found")
    role = group_service.get_member_role(db, group_id, current_user.id)
    if role is None and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    return group_service.get_members(db, group_id)


@router.post("/groups/{group_id}/members", response_model=GroupMemberResponse, status_code=201)
async def add_group_member(
    group_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    role = group_service.get_member_role(db, group_id, current_user.id)
    if role not in ("admin", "moderator"):
        raise HTTPException(status_code=403, detail="Only admins and moderators can add members")
    return group_service.add_member(db, group_id, user_id)


@router.delete("/groups/{group_id}/members/{user_id}", status_code=204)
async def remove_group_member(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    role = group_service.get_member_role(db, group_id, current_user.id)
    if role not in ("admin", "moderator") and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to remove this member")
    group_service.remove_member(db, group_id, user_id)


@router.put("/groups/{group_id}/members/{user_id}/role")
async def update_group_member_role(
    group_id: int,
    user_id: int,
    role: str = Query(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    admin_role = group_service.get_member_role(db, group_id, current_user.id)
    if admin_role != "admin":
        raise HTTPException(status_code=403, detail="Only group admins can change roles")
    return group_service.update_member_role(db, group_id, user_id, role)


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------


async def _get_user_from_token(token: str, db: Session) -> UserModel | None:
    result = validate_access_token(db, token)
    if result is None:
        return None
    user_id, _session = result
    return user_service.get(db, user_id)


@router.websocket("/ws")
async def chat_websocket(ws: WebSocket, token: str = Query(None), db: Session = Depends(get_db)):
    # Prefer Sec-WebSocket-Protocol header over query param to avoid
    # token leakage in URLs (proxy logs, browser history, etc.).
    protocols = ws.headers.get("sec-websocket-protocol", "")
    if protocols:
        token = protocols.split(", ")[0].strip()
    if not token:
        await ws.close(code=4001, reason="Missing authentication token")
        return
    user = await _get_user_from_token(token, db)
    if user is None:
        await ws.close(code=4001, reason="Invalid or expired token")
        return

    backend = chat_backend_registry.backend
    manager = getattr(backend, "manager", None)
    if manager is None:
        await ws.close(code=4003, reason="Real-time chat not available")
        return

    await manager.connect(user.id, ws, subprotocol=token)

    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")

            if msg_type == "ping":
                await ws.send_json({"type": "pong"})

            elif msg_type == "typing":
                receiver_id = data.get("receiver_id")
                channel_id = data.get("channel_id")
                group_id = data.get("group_id")
                if channel_id:
                    members = channel_service.get_members(db, channel_id)
                    if not any(m.user_id == user.id for m in members):
                        continue
                    for m in members:
                        if m.user_id != user.id:
                            await manager.broadcast(
                                m.user_id,
                                {
                                    "type": "typing",
                                    "sender_id": user.id,
                                    "channel_id": channel_id,
                                },
                            )
                elif group_id:
                    members = group_service.get_members(db, group_id)
                    if not any(m.user_id == user.id for m in members):
                        continue
                    for m in members:
                        if m.user_id != user.id:
                            await manager.broadcast(
                                m.user_id,
                                {
                                    "type": "typing",
                                    "sender_id": user.id,
                                    "group_id": group_id,
                                },
                            )
                elif receiver_id:
                    await manager.broadcast(
                        receiver_id,
                        {
                            "type": "typing",
                            "sender_id": user.id,
                        },
                    )

            elif msg_type == "subscribe_channel":
                channel_id = data.get("channel_id")
                if channel_id:
                    logger.info("User %d subscribing to channel %d events", user.id, channel_id)

            else:
                logger.warning("Unknown WS message type=%s from user=%d", msg_type, user.id)

    except WebSocketDisconnect:
        manager.disconnect(user.id, ws)
    except Exception as exc:
        logger.error("WS error for user=%d: %s", user.id, exc)
        manager.disconnect(user.id, ws)
