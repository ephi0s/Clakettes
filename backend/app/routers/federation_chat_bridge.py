import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.chat_backend.registry import chat_backend_registry
from app.config import settings
from app.database import get_db
from app.models.message import Message
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.channel_service import ChannelService
from app.services.message_federation_service import SIGNED_FIELDS, message_federation_service
from app.services.message_queue_service import ChatOutbox, MessageQueueService
from app.services.user_service import UserService

router = APIRouter(prefix="/federation", tags=["federation-chat-bridge"])
queue = MessageQueueService()
federation = message_federation_service


class InboundEnvelope(BaseModel):
    message_id: str
    node_origin: str
    channel_id: int | None = None
    receiver_id: int | None = None
    content: str
    timestamp: str
    signature: str


class OutboundEnvelope(BaseModel):
    target_node: str
    channel_id: int | None = None
    receiver_id: int | None = None
    content: str


def _resolve_sender(db: Session, node_origin: str) -> User:
    sender = db.query(User).filter((User.handle == node_origin) | (User.username == node_origin)).first()
    if sender is not None:
        return sender
    sender = db.query(User).first()
    if sender is not None:
        return sender
    safe = "".join(c if c.isalnum() or c in ".-" else "-" for c in node_origin)[:40] or "peer"
    return UserService().create(
        db,
        UserCreate(
            username=f"fed-{safe}",
            email=f"fed-{safe}@federated.local",
            full_name=node_origin,
            role="user",
            password=uuid.uuid4().hex,
        ),
    )


async def _broadcast(db: Session, envelope: dict[str, Any], sender_id: int) -> None:
    try:
        backend = chat_backend_registry.backend
    except RuntimeError:
        return
    kwargs = dict(
        message_id=envelope.get("db_message_id", 0),
        sender_id=sender_id,
        group_id=None,
        content=envelope.get("content", ""),
        message_type="text",
        **{k: envelope.get(k) for k in ("channel_id", "media_url", "latitude", "longitude", "created_at")},
    )
    if envelope.get("channel_id") is not None:
        for member in ChannelService().get_members(db, envelope["channel_id"]):
            if member.user_id != sender_id:
                await backend.send_message(receiver_id=member.user_id, **kwargs)
    elif envelope.get("receiver_id") is not None:
        await backend.send_message(receiver_id=envelope["receiver_id"], **kwargs)


@router.post("/chat/bridge/inbound")
async def chat_bridge_inbound(body: InboundEnvelope, db: Session = Depends(get_db)):
    if not federation.is_node_permitted(db, body.node_origin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="node_not_permitted")
    if body.channel_id is None and body.receiver_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="channel_id_or_receiver_id_required")

    public_pem = await federation.fetch_peer_public_key_pem(body.node_origin)
    if not public_pem or not federation.verify(body.model_dump(), public_pem):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid_signature")

    existing = queue.get_by_message_id(db, body.message_id)
    if existing is not None:
        return {"status": "duplicate", "duplicate": True, "message_id": body.message_id}

    sender = _resolve_sender(db, body.node_origin)
    msg = Message(
        content=body.content,
        sender_id=sender.id,
        receiver_id=body.receiver_id,
        group_id=None,
        channel_id=body.channel_id,
        message_type="text",
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    payload = body.model_dump()
    payload["db_message_id"] = msg.id
    outbox = queue.enqueue(
        db,
        message_id=body.message_id,
        node_origin=body.node_origin,
        subject="federation.inbound",
        payload=payload,
        signature=body.signature,
    )
    queue.mark_sent(db, outbox.id)
    await _broadcast(db, payload, sender.id)
    return {"status": "accepted", "duplicate": False, "message_id": body.message_id, "db_message_id": msg.id}


@router.post("/chat/bridge/outbound")
async def chat_bridge_outbound(body: OutboundEnvelope, db: Session = Depends(get_db)):
    fields: dict[str, Any] = {
        "message_id": str(uuid.uuid4()),
        "node_origin": federation.local_node(),
        "channel_id": body.channel_id,
        "receiver_id": body.receiver_id,
        "content": body.content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    fields = {k: fields.get(k) for k in SIGNED_FIELDS}
    signature = federation.sign(fields)
    subject = f"clakettes.chat.node.{body.target_node}"
    outbox = queue.enqueue(
        db,
        message_id=fields["message_id"],
        node_origin=body.target_node,
        subject=subject,
        payload=fields,
        signature=signature,
    )
    envelope = {
        "message_id": outbox.message_id,
        "node_origin": outbox.node_origin,
        "subject": outbox.subject,
        "payload": outbox.payload,
        "signature": outbox.signature,
    }
    state = "sent"
    try:
        await queue._transport.publish(envelope)
        queue.mark_sent(db, outbox.id)
    except Exception as exc:
        state = "failed"
        queue.mark_failed(db, outbox.id, f"{type(exc).__name__}: {exc}")
    return {"status": state, "message_id": outbox.message_id, "node_origin": outbox.node_origin, "subject": subject}


@router.get("/chat/bridge/config")
async def chat_bridge_config(db: Session = Depends(get_db)):
    nodes = (
        db.query(ChatOutbox.node_origin)
        .filter(ChatOutbox.subject == "federation.inbound")
        .distinct()
        .order_by(ChatOutbox.node_origin.asc())
        .all()
    )
    return {
        "transport": "nats-jetstream",
        "stream": "CLAKETTES_EVENTS",
        "mtls_required": bool(getattr(settings, "MTLS_REQUIRED", False)),
        "signature_algorithm": "RS256",
        "signed_fields": list(SIGNED_FIELDS),
        "subject_mapping": {
            "default": "clakettes.chat.{channel_id}",
            "direct": "clakettes.chat.direct.{receiver_id}",
            "bridge": "clakettes.chat.node.{node_origin}",
        },
        "node_subjects": {row.node_origin: f"clakettes.chat.node.{row.node_origin}" for row in nodes},
    }


@router.get("/chat/messages")
async def federation_chat_messages(node: str | None = None, db: Session = Depends(get_db)):
    query = db.query(ChatOutbox).filter(ChatOutbox.subject == "federation.inbound")
    if node is not None:
        query = query.filter(ChatOutbox.node_origin == node)
    seen: set[str] = set()
    items: list[dict[str, Any]] = []
    for row in query.all():
        if row.message_id in seen:
            continue
        seen.add(row.message_id)
        payload = row.payload or {}
        items.append(
            {
                "message_id": row.message_id,
                "node_origin": row.node_origin,
                "timestamp": payload.get("timestamp"),
                "db_message_id": payload.get("db_message_id"),
                "channel_id": payload.get("channel_id"),
                "receiver_id": payload.get("receiver_id"),
                "content": payload.get("content"),
            }
        )
    items.sort(key=lambda item: (item["timestamp"] or "", item["message_id"]))
    return {"messages": items}
