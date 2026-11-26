import asyncio
import hashlib
import hmac
import json
from datetime import datetime, timezone

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
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
    scheme = "https" if settings.is_production or settings.MTLS_REQUIRED else "http"
    return f"{scheme}://{domain}/api/federation/events/publish"


def _local_node_domain():
    base = getattr(settings, "PUBLIC_BASE_URL", None) or "primary"
    return str(base).replace("https://", "").replace("http://", "").rstrip("/")


def _event_signature(body):
    return hmac.new(str(settings.SECRET_KEY).encode("utf-8"), body, hashlib.sha256).hexdigest()


def _peer_token(domain):
    from app.routers.federation import federation_token_service

    return federation_token_service.create_token(
        "federation-events",
        extra_claims={"iss": domain, "issuer_node": domain},
    )


def _require_trusted_node(db, domain):
    node = NodePeeringService().get_by_domain(db, domain)
    if node is None or not node.allowed or getattr(node, "revoked_at", None) is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="peer node not trusted")
    return node


async def _request_peer(request, db):
    peer = getattr(request.state, "peer_node", None)
    if peer is not None:
        return getattr(peer, "node_domain", None)
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:].strip()
    try:
        claims = jwt.decode(token, options={"verify_signature": False})
    except jwt.PyJWTError:
        return None
    if claims.get("typ") != "federation" or claims.get("aud") != "clakettes-federation":
        return None
    issuer = claims.get("iss")
    if not isinstance(issuer, str) or not issuer.strip():
        return None
    _require_trusted_node(db, issuer)
    from app.routers.federation import get_current_federation_peer

    verified = await get_current_federation_peer(request)
    if verified is None or verified.get("iss") != issuer:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid federation peer token")
    claimed = verified.get("issuer_node") or issuer
    if claimed != issuer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="peer node mismatch")
    return issuer


async def _send_to_peer(domain, envelope):
    issuer = _local_node_domain()
    payload = {
        "event": envelope,
        "issuer": issuer,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Clakettes-Signature": _event_signature(body),
        "Authorization": f"Bearer {_peer_token(issuer)}",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            _peer_url(domain),
            content=body,
            headers=headers,
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
    request: Request,
    topic: str = Query(CACHE_INVALIDATION_TOPIC),
    since: int = Query(0, ge=0),
    token: str | None = Query(None, deprecated=True),
    limit: int | None = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    authorization = request.headers.get("authorization", "")
    bearer = authorization[7:].strip() if authorization.startswith("Bearer ") else ""
    token_to_validate = bearer or token
    if not token_to_validate:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    result = validate_access_token(db, token_to_validate)
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
    request: Request,
    db: Session = Depends(get_db),
):
    peer_domain = await _request_peer(request, db)
    if peer_domain:
        raw = await request.body()
        signature = request.headers.get("x-clakettes-signature")
        if not signature or not hmac.compare_digest(_event_signature(raw), signature):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid event signature")
        _require_trusted_node(db, peer_domain)
        try:
            payload = json.loads(raw)
        except (ValueError, TypeError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid payload")
        if payload.get("issuer") not in (None, peer_domain):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="issuer mismatch")
        if body.node and body.node != peer_domain:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="node mismatch")
        body.node = peer_domain
    else:
        auth = request.headers.get("authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        current_user = await get_current_user(token=auth[7:].strip(), db=db)
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
