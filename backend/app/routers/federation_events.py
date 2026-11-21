import asyncio
import hashlib
import hmac
import json
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.auth import get_current_user, validate_access_token
from app.config import settings
from app.database import get_db
from app.routers.permissions import require_admin
from app.services.event_bus_service import CACHE_INVALIDATION_TOPIC, entity_topic, event_bus, node_topic
from app.services.node_peering_service import NodePeeringService

router = APIRouter(prefix="/api/federation/events", tags=["federation-events"])
_worker_task = None


class EventPublishIn(BaseModel):
    type: str
    topic: str | None = None
    node: str | None = None
    entity: str | None = None
    entity_id: str | None = None
    data: dict = Field(default_factory=dict)


def _derive_topic(body):
    if body.topic:
        return body.topic
    parts = []
    if body.node:
        parts.append(node_topic(body.node))
    if body.entity:
        parts.append(entity_topic(body.entity, body.entity_id))
    return ":".join(parts) if parts else CACHE_INVALIDATION_TOPIC


def _event_category(envelope):
    value = f"{envelope.get('type', '')} {envelope.get('topic', '')}".lower()
    if "chat" in value or "message" in value:
        return "chat"
    if "search" in value or "index" in value:
        return "search"
    return None


def _peer_disabled(node, envelope, db):
    category = _event_category(envelope)
    if category is None:
        return False
    if getattr(node, f"disable_{category}", False):
        return True
    if f"disable_{category}" in (node.capabilities or []):
        return True
    try:
        if "node_policies" in inspect(db.bind).get_table_names():
            row = db.execute(
                text("SELECT disable_chat, disable_search FROM node_policies WHERE node_domain = :domain"),
                {"domain": node.node_domain},
            ).first()
            if row is not None:
                return bool(row[0] if category == "chat" else row[1])
    except Exception:
        pass
    return False


def _peer_url(domain):
    scheme = "https" if getattr(settings, "MTLS_REQUIRED", False) else "http"
    return f"{scheme}://{domain}/api/federation/events/publish"


async def _send_to_peer(domain, envelope):
    payload = {
        "event": envelope,
        "issuer": getattr(settings, "PUBLIC_BASE_URL", None) or "primary",
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(str(settings.SECRET_KEY).encode("utf-8"), body, hashlib.sha256).hexdigest()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            _peer_url(domain),
            content=body,
            headers={"Content-Type": "application/json", "X-Clakettes-Signature": signature},
            timeout=5.0,
        )
        response.raise_for_status()
    return True


async def _retry_worker():
    while True:
        for item in event_bus.due_retries():
            try:
                await _send_to_peer(item["node_domain"], item["event"])
                event_bus.acknowledge_retry(item["id"])
            except Exception as exc:
                event_bus.fail_retry(item["id"], str(exc))
        await asyncio.sleep(0.2)


def _ensure_worker():
    global _worker_task
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.create_task(_retry_worker())


def _sse_frame(envelope):
    return f"event: {envelope['type']}\ndata: {json.dumps(envelope, ensure_ascii=False)}\n\n"


@router.get("/stream")
async def stream_events(
    topic: str = Query(CACHE_INVALIDATION_TOPIC),
    since: int = Query(0, ge=0),
    token: str = Query(...),
    limit: int | None = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    result = validate_access_token(db, token)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    sub_id, queue = event_bus.subscribe(topic)
    replayed = event_bus.replay(topic, since)
    seen = {event["seq"] for event in replayed}

    async def generator():
        delivered_count = 0
        try:
            yield ": connected\n\n"
            for event in replayed:
                yield _sse_frame(event)
                delivered_count += 1
                if limit is not None and delivered_count >= limit:
                    return
            while limit is None or delivered_count < limit:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15)
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
                    continue
                if event["seq"] in seen:
                    continue
                seen.add(event["seq"])
                yield _sse_frame(event)
                delivered_count += 1
        finally:
            event_bus.unsubscribe(topic, sub_id)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/publish")
async def publish_event(
    body: EventPublishIn,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_admin(current_user, db)
    topic = _derive_topic(body)
    envelope = event_bus.publish(topic, {"type": body.type, "node": body.node, "data": body.data})

    delivered = []
    failed = []
    skipped = []
    for node in NodePeeringService().list_allowed(db):
        if _peer_disabled(node, envelope, db):
            skipped.append(node.node_domain)
            continue
        try:
            await _send_to_peer(node.node_domain, envelope)
            delivered.append(node.node_domain)
        except Exception as exc:
            failed.append(node.node_domain)
            event_bus.enqueue_retry(node.node_domain, envelope, str(exc))
    if failed:
        _ensure_worker()
    return {
        "published": True,
        "topic": topic,
        "seq": envelope["seq"],
        "delivered": delivered,
        "failed": failed,
        "skipped": skipped,
        "retry_queued": len(failed),
    }


@router.get("/retry-queue")
async def retry_queue_status(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    require_admin(current_user, db)
    pending = event_bus.list_retries()
    return {"pending": pending, "count": len(pending)}
