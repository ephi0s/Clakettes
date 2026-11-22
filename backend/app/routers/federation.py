"""Federation endpoints (node policies: allowlist/blocklist)."""

import base64
import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timedelta, timezone

import httpx
import jwt
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.trusted_node import TrustedNode
from app.auth import get_current_user, validate_access_token
from app.rate_limiter import RateLimiter
from app.services.node_policy_service import NodePolicyService
from app.services.user_service import UserService
from app.services.moderation_report_service import ModerationReportService
from app.services.node_peering_service import NodePeeringService
from app.config import settings
from app.services.federation_token_service import FederationTokenService
from app.services.message_queue_service import canonical_json
from app.services.portability_service import PortabilityService
from app.services.event_bus_service import entity_topic, event_bus, node_topic
from app.routers import federation_chat_bridge, federation_resilience
from app.routers import federation_events as federation_events_router

federation_token_service = FederationTokenService()

_federation_limiter = RateLimiter()


def _signing_key():
    key_path = getattr(settings, "MTLS_CLIENT_KEY_PATH", None) or os.environ.get("MTLS_CLIENT_KEY_PATH")
    if key_path and os.path.isfile(key_path):
        with open(key_path, "rb") as fh:
            return serialization.load_pem_private_key(fh.read(), password=None)
    return serialization.load_pem_private_key(federation_token_service.private_pem().encode("ascii"), password=None)


def _manifest_signature_payload(manifest: dict) -> dict:
    return {k: v for k, v in manifest.items() if k not in ("signature", "certificate_chain")}


def _canonical_json(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _utc_naive(value: datetime) -> datetime:
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


async def _fetch_peer_jwks(issuer: str) -> dict:
    jwks_url = f"https://{issuer}/api/federation/.well-known/jwks.json"
    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url, timeout=10)
        response.raise_for_status()
        return response.json()


def _check_federation_rate_limit(request: Request):
    if os.environ.get("TESTING", "").lower() in ("true", "1"):
        return
    ip = request.client.host if request.client else "unknown"
    if not _federation_limiter.check(f"federation:{ip}", 60, 60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many federation requests. Try again later.",
        )


router = APIRouter(prefix="/federation", tags=["federation"], dependencies=[Depends(_check_federation_rate_limit)])
service = NodePolicyService()
report_service = ModerationReportService()
portability_service = PortabilityService()
user_service = UserService()


class NodePolicyIn(BaseModel):
    node_domain: str
    allowed: bool = True
    consent_required: bool = True
    minimize_data: bool = True
    import_only: bool = False
    disable_chat: bool = False
    disable_search: bool = False
    reason: str | None = None


class NodeRegisterIn(BaseModel):
    node_domain: str
    fingerprint_sha256: str
    subject_cn: str | None = None
    capabilities: list[str] | None = None
    allowed: bool = True


def _require_peer(request: Request) -> TrustedNode | None:
    """Exige identidad de nodo verificada vía mTLS cuando MTLS_REQUIRED está activo.

    En desarrollo (MTLS_REQUIRED=False) devuelve None sin bloquear, para no romper
    los placeholders de prueba. En producción, rechaza si no hay peer verificado.
    """
    if not settings.MTLS_REQUIRED:
        return None
    peer = getattr(request.state, "peer_node", None)
    if peer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="mTLS peer identity required",
        )
    return peer


def _require_admin(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")


async def _resolve_peer_node(request: Request, claimed: str | None = None) -> str:
    peer = getattr(request.state, "peer_node", None)
    domain = getattr(peer, "node_domain", None) if peer is not None else None
    if not domain:
        token_peer = await get_current_federation_peer(request)
        if token_peer is not None:
            domain = token_peer.get("issuer_node") or token_peer.get("iss")
    claimed = claimed.strip() if isinstance(claimed, str) else ""
    if domain and claimed and domain != claimed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puede actuar en nombre de otro nodo")
    node = domain or claimed
    if not node:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="node required")
    return node


def _ref_domain(ref: str) -> str | None:
    if "@" in ref:
        return ref.rsplit("@", 1)[1].strip().lower() or None
    parts = ref.split(":")
    if len(parts) >= 4 and parts[0] == "did" and parts[1] == "clakettes":
        return parts[2].strip().lower() or None
    return None


@router.get("/nodes")
async def list_node_policies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require_admin(current_user)
    return [
        {
            "id": p.id,
            "node_domain": p.node_domain,
            "allowed": p.allowed,
            "consent_required": p.consent_required,
            "minimize_data": p.minimize_data,
            "import_only": p.import_only,
            "disable_chat": p.disable_chat,
            "disable_search": p.disable_search,
            "reason": p.reason,
        }
        for p in service.list_policies(db)
    ]


@router.post("/nodes")
async def set_node_policy(
    body: NodePolicyIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    _require_admin(current_user)
    p = service.set_policy(
        db,
        body.node_domain,
        body.allowed,
        body.consent_required,
        body.minimize_data,
        body.import_only,
        body.disable_chat,
        body.disable_search,
        body.reason,
    )
    return {
        "id": p.id,
        "node_domain": p.node_domain,
        "allowed": p.allowed,
        "consent_required": p.consent_required,
        "minimize_data": p.minimize_data,
        "import_only": p.import_only,
        "disable_chat": p.disable_chat,
        "disable_search": p.disable_search,
        "reason": p.reason,
    }


@router.get("/manifest")
async def federation_manifest():
    now = datetime.now(timezone.utc)
    manifest = {
        "schema_version": "1",
        "node": settings.PUBLIC_BASE_URL or "primary",
        "version": "1.0.0",
        "capabilities": ["festivals", "users", "chat", "voting"],
        "issued_at": now.isoformat(),
        "expires_at": (now + timedelta(hours=24)).isoformat(),
    }
    signature = _signing_key().sign(_canonical_json(manifest), padding.PKCS1v15(), hashes.SHA256())
    manifest["signature"] = base64.b64encode(signature).decode("ascii")
    chain = []
    cert_path = getattr(settings, "MTLS_CLIENT_CERT_PATH", None) or os.environ.get("MTLS_CLIENT_CERT_PATH")
    if cert_path and os.path.isfile(cert_path):
        with open(cert_path, "r", encoding="utf-8") as fh:
            chain.append(fh.read())
    manifest["certificate_chain"] = chain
    return manifest


@router.patch("/reports/{report_id}")
async def update_report_status(report_id: int, status: str, db: Session = Depends(get_db)):
    r = report_service.update_status(db, report_id, status)
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"id": r.id, "status": r.status}


@router.get("/directory")
async def federation_directory(db: Session = Depends(get_db)):
    nodes = NodePeeringService().list_allowed(db)
    return {
        "nodes": [
            {
                "domain": n.node_domain,
                "schema_version": "1",
                "status": "online" if n.last_seen_at else "unknown",
                "version": "1.0.0",
                "last_seen": n.last_seen_at.isoformat() if n.last_seen_at else None,
                "cert_fingerprint_sha256": n.cert_fingerprint_sha256,
                "capabilities": n.capabilities or [],
                "consent_required": n.consent_required,
                "minimize_data": n.minimize_data,
            }
            for n in nodes
        ]
    }


class ReportIn(BaseModel):
    reporter_node: str
    target_node: str
    reason: str
    target_user_ref: str | None = None


@router.post("/reports")
async def create_report(body: ReportIn, db: Session = Depends(get_db)):
    r = report_service.create(db, body.reporter_node, body.target_node, body.reason, body.target_user_ref)
    return {"id": r.id, "status": r.status}


@router.get("/reports")
async def list_reports(node: str, db: Session = Depends(get_db)):
    return [
        {
            "id": r.id,
            "reporter_node": r.reporter_node,
            "target_node": r.target_node,
            "reason": r.reason,
            "status": r.status,
        }
        for r in report_service.list_for_node(db, node)
    ]


@router.delete("/users/{user_ref}")
async def propagate_erase(request: Request, user_ref: str, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(
            (User.uuid == user_ref) | (User.did == user_ref) | (User.handle == user_ref) | (User.username == user_ref)
        )
        .first()
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    authorized = False
    auth = request.headers.get("authorization", "")
    token = auth[7:].strip() if auth.startswith("Bearer ") else None
    if token:
        result = validate_access_token(db, token)
        if result is not None:
            app_user = db.query(User).filter(User.id == result[0]).first()
            if app_user is not None and (app_user.id == user.id or app_user.role == "admin"):
                authorized = True

    if not authorized:
        peer_domain = None
        peer = getattr(request.state, "peer_node", None)
        if peer is not None:
            peer_domain = getattr(peer, "node_domain", None)
        if not peer_domain:
            token_peer = await get_current_federation_peer(request)
            if token_peer is not None:
                peer_domain = token_peer.get("issuer_node") or token_peer.get("iss")
        ref_domain = _ref_domain(user_ref)
        if (
            isinstance(peer_domain, str)
            and peer_domain.strip()
            and ref_domain is not None
            and peer_domain.strip().lower() == ref_domain
            and service.is_allowed(db, peer_domain)
        ):
            authorized = True

    if not authorized:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to erase this user")

    user_id = user.id
    user_uuid = user.uuid
    user_did = user.did
    user_handle = user.handle
    try:
        summary = user_service.erase_personal_data(db, user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    origin = getattr(settings, "PUBLIC_BASE_URL", None) or "primary"
    topic = ":".join([node_topic(origin), entity_topic("user", str(user_id))])
    try:
        envelope = event_bus.publish(
            topic,
            {
                "type": "user.erase",
                "node": origin,
                "data": {
                    "ref": user_ref,
                    "user_id": user_id,
                    "uuid": user_uuid,
                    "did": user_did,
                    "handle": user_handle,
                },
            },
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="event bus unavailable")

    propagated = []
    failed = []
    for node in NodePeeringService().list_allowed(db):
        if node.node_domain == origin:
            continue
        try:
            await federation_events_router._send_to_peer(node.node_domain, envelope)
            propagated.append(node.node_domain)
        except Exception as exc:
            failed.append(node.node_domain)
            event_bus.enqueue_retry(node.node_domain, envelope, str(exc))
    if failed:
        federation_events_router._ensure_worker()

    return {
        "erased": True,
        "ref": user_ref,
        "user_id": user_id,
        "summary": summary,
        "propagated": propagated,
        "failed": failed,
    }


@router.get("/export/{user_ref}")
async def export_bundle(user_ref: str, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(
            (User.uuid == user_ref) | (User.did == user_ref) | (User.handle == user_ref) | (User.username == user_ref)
        )
        .first()
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    try:
        return portability_service.create_bundle(db, user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/health", deprecated=True)
async def federation_health():
    return {"status": "ok", "node": "primary"}


@router.post("/verify")
async def verify_bundle(bundle: dict):
    if not isinstance(bundle, dict):
        return {"valid": False, "checksum": None, "detail": "invalid_bundle"}

    if bundle.get("bundle_version") == PortabilityService.BUNDLE_VERSION and isinstance(bundle.get("payload"), dict):
        valid = portability_service.verify_bundle(bundle)
        return {
            "valid": valid,
            "checksum": bundle.get("checksum"),
            "detail": "ok" if valid else "integrity_check_failed",
        }

    payload = bundle.get("payload")
    if not isinstance(payload, dict):
        payload = {
            k: v
            for k, v in bundle.items()
            if k not in ("signature", "checksum", "certificate_chain", "public_key", "fingerprint")
        }

    checksum = hashlib.sha256(canonical_json(payload)).hexdigest()
    provided_checksum = bundle.get("checksum")
    signature = bundle.get("signature")

    if provided_checksum is None and not signature:
        return {"valid": False, "checksum": checksum, "detail": "no_cryptographic_material"}

    if provided_checksum is not None and not hmac.compare_digest(checksum, str(provided_checksum)):
        return {"valid": False, "checksum": checksum, "detail": "checksum_mismatch"}

    if signature:
        try:
            chain = bundle.get("certificate_chain")
            if isinstance(chain, list) and chain:
                cert_pem = str(chain[0])
            elif isinstance(chain, str) and chain:
                cert_pem = chain
            else:
                cert_pem = None
            if cert_pem is not None:
                from app.mtls import cert_fingerprint_sha256

                fingerprint = bundle.get("fingerprint")
                if fingerprint is not None and not hmac.compare_digest(
                    cert_fingerprint_sha256(cert_pem), str(fingerprint)
                ):
                    return {"valid": False, "checksum": checksum, "detail": "fingerprint_mismatch"}
                public_key = x509.load_pem_x509_certificate(cert_pem.encode("ascii")).public_key()
            elif bundle.get("public_key"):
                public_key = serialization.load_pem_public_key(str(bundle["public_key"]).encode("ascii"))
            else:
                return {"valid": False, "checksum": checksum, "detail": "verification_key_missing"}
            public_key.verify(base64.b64decode(signature), canonical_json(payload), padding.PKCS1v15(), hashes.SHA256())
        except Exception:
            return {"valid": False, "checksum": checksum, "detail": "signature_invalid"}

    return {"valid": True, "checksum": checksum, "detail": "ok"}


@router.post("/publish")
async def publish_event(event: dict, request: Request):
    if not isinstance(event, dict) or not event:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="event must be a non-empty object")
    event_type = event.get("type")
    if not isinstance(event_type, str) or not event_type.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="event.type required")
    data = event.get("data", {})
    if not isinstance(data, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="event.data must be an object")

    origin = None
    peer = getattr(request.state, "peer_node", None)
    if peer is not None:
        origin = getattr(peer, "node_domain", None)
    if origin is None:
        federated_peer = await get_current_federation_peer(request)
        if federated_peer is not None:
            origin = federated_peer.get("issuer_node") or federated_peer.get("iss")
    if not isinstance(origin, str) or not origin.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="origin node required")

    topic = event.get("topic")
    if topic is not None and (not isinstance(topic, str) or not topic.strip()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="event.topic must be a string")
    if not topic:
        parts = [node_topic(origin)]
        entity = event.get("entity")
        if isinstance(entity, str) and entity.strip():
            entity_id = event.get("entity_id")
            parts.append(entity_topic(entity, entity_id if isinstance(entity_id, str) else None))
        topic = ":".join(parts)

    try:
        envelope = event_bus.publish(topic, {"type": event_type, "node": origin, "data": data})
    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="event bus unavailable")

    return {
        "published": True,
        "topic": topic,
        "seq": envelope["seq"],
        "delivered": [],
        "failed": [],
        "skipped": [],
        "retry_queued": 0,
    }


class NodeRecoverIn(BaseModel):
    node: str


async def _recover_federation_node(node_domain: str, db: Session):
    target = federation_resilience.peering.get_by_domain(db, node_domain)
    if target is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"node": node_domain, "status": "not_found", "message": "Nodo no encontrado"},
        )

    incident = federation_resilience.clear_revocation(db, node_domain)

    federation_resilience.peering.restore(db, node_domain)
    target.last_seen_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(target)

    pending_retries = len([r for r in event_bus.list_retries() if r.get("node_domain") == node_domain])
    if pending_retries:
        federation_events_router._ensure_worker()
    federation_resilience.metrics.record(node_domain, 0.0, True, retries=pending_retries)

    return {
        "node": node_domain,
        "status": "recovering" if pending_retries else "recovered",
        "incident_cleared": incident is not None,
        "allowed": target.allowed,
        "pending_retries": pending_retries,
    }


@router.post("/recover")
async def recover_node(body: NodeRecoverIn, request: Request, db: Session = Depends(get_db)):
    node_domain = await _resolve_peer_node(request, body.node)
    return await _recover_federation_node(node_domain, db)


@router.post("/bridge")
async def bridge_chat(message: dict, request: Request, db: Session = Depends(get_db)):
    if not isinstance(message, dict) or not message:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="message must be a non-empty object")

    origin = None
    peer = getattr(request.state, "peer_node", None)
    if peer is not None:
        origin = getattr(peer, "node_domain", None)
    if origin is None:
        federated_peer = await get_current_federation_peer(request)
        if federated_peer is not None:
            origin = federated_peer.get("issuer_node") or federated_peer.get("iss")
    if not isinstance(origin, str) or not origin.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="origin node required")

    target_node = message.get("target_node")
    if target_node is None:
        target_node = message.get("target")
    if not isinstance(target_node, str) or not target_node.strip():
        target_node = origin

    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="content required")

    channel_id = message.get("channel_id")
    if channel_id is not None and (not isinstance(channel_id, int) or isinstance(channel_id, bool)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="channel_id must be an integer")
    receiver_id = message.get("receiver_id")
    if receiver_id is not None and (not isinstance(receiver_id, int) or isinstance(receiver_id, bool)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="receiver_id must be an integer")

    body = federation_chat_bridge.OutboundEnvelope(
        target_node=target_node,
        channel_id=channel_id,
        receiver_id=receiver_id,
        content=content,
    )
    try:
        result = await federation_chat_bridge.chat_bridge_outbound(body, db)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="chat bridge unavailable")
    if result.get("status") != "sent":
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="chat bridge unavailable")
    return result


@router.get("/aggregate-nodes", deprecated=True)
async def aggregate_nodes():
    return {"nodes": 1, "results": []}


@router.get("/keys", deprecated=True)
async def peering_keys():
    return {"keys": []}


@router.get("/events", deprecated=True)
async def federation_events():
    return {"events": []}


@router.get("/capabilities", deprecated=True)
async def federation_capabilities():
    return {"capabilities": ["festivals", "users", "chat", "voting"]}


@router.get("/status", deprecated=True)
async def federation_status():
    return {"status": "running"}


@router.get("/info", deprecated=True)
async def federation_info():
    return {"name": "Clakettes", "version": "1.0"}


@router.get("/ping", deprecated=True)
async def federation_ping():
    return {"pong": True}


@router.post("/echo")
async def federation_echo(payload: dict):
    return {"echo": payload}


@router.get("/time")
async def federation_time():
    from datetime import datetime, timezone

    return {"time": datetime.now(timezone.utc).isoformat()}


@router.get("/version", deprecated=True)
async def federation_version():
    return {"version": "1.0.0"}


@router.post("/checksum")
async def federation_checksum(payload: dict):
    return {"checksum": hashlib.sha256(canonical_json(payload)).hexdigest(), "size": len(str(payload))}


@router.post("/notify", deprecated=True)
async def federation_notify(payload: dict):
    return {"notified": True}


@router.post("/subscribe", deprecated=True)
async def federation_subscribe(payload: dict):
    return {"subscribed": True}


@router.post("/unsubscribe", deprecated=True)
async def federation_unsubscribe(payload: dict):
    return {"unsubscribed": True}


@router.get("/discover", deprecated=True)
async def federation_discover():
    return {"discovered": []}


@router.post("/register")
async def federation_register(body: NodeRegisterIn, db: Session = Depends(get_db)):
    """Registra o actualiza un nodo federado (dominio + huella de cert + capacidades).

    Es el punto de entrada del directorio de nodos: tras el handshake mTLS, cada
    nodo se anuncia aquí para aparecer en GET /federation/directory.
    """
    node = NodePeeringService().register_or_update(
        db,
        body.node_domain,
        body.fingerprint_sha256,
        subject_cn=body.subject_cn,
        capabilities=body.capabilities,
        allowed=body.allowed,
    )
    return {
        "node_domain": node.node_domain,
        "fingerprint_sha256": node.cert_fingerprint_sha256,
        "subject_cn": node.cert_subject_cn,
        "allowed": node.allowed,
        "capabilities": node.capabilities or [],
        "last_seen": node.last_seen_at.isoformat() if node.last_seen_at else None,
        "registered": True,
    }


@router.post("/unregister")
async def federation_unregister(payload: dict, request: Request, db: Session = Depends(get_db)):
    claimed = payload.get("node") or payload.get("node_domain") if isinstance(payload, dict) else None
    node_domain = await _resolve_peer_node(request, claimed)
    peering = NodePeeringService()
    if peering.get_by_domain(db, node_domain) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nodo no encontrado")
    peering.revoke(db, node_domain)
    federation_resilience.record_revocation(
        db,
        node_domain,
        reason=payload.get("reason") if isinstance(payload, dict) else None,
        revoked_by=node_domain,
    )
    federation_resilience.metrics.record(node_domain, 0.0, True)
    return {"node": node_domain, "unregistered": True, "allowed": False}


@router.post("/sync")
async def federation_sync(payload: dict, request: Request):
    claimed = payload.get("node") or payload.get("node_domain") if isinstance(payload, dict) else None
    node_domain = await _resolve_peer_node(request, claimed)
    since = payload.get("since", 0) if isinstance(payload, dict) else 0
    if isinstance(since, bool) or not isinstance(since, int) or since < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="since must be a non-negative integer")
    topic = payload.get("topic") if isinstance(payload, dict) else None
    if topic is not None and (not isinstance(topic, str) or not topic.strip()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="topic must be a string")
    topic = topic or node_topic(node_domain)
    return {
        "synced": True,
        "node": node_domain,
        "topic": topic,
        "since": since,
        "latest": event_bus.latest_sequence(topic),
        "events": event_bus.replay(topic, since),
    }


@router.post("/reconcile")
async def federation_reconcile(payload: dict, request: Request, db: Session = Depends(get_db)):
    claimed = payload.get("node") or payload.get("node_domain") if isinstance(payload, dict) else None
    node_domain = await _resolve_peer_node(request, claimed)
    peering = NodePeeringService()
    node = peering.get_by_domain(db, node_domain)
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nodo no encontrado")
    policy_allowed = service.is_allowed(db, node_domain)
    changed = False
    if not policy_allowed and node.allowed:
        peering.revoke(db, node_domain)
        federation_resilience.record_revocation(
            db,
            node_domain,
            reason="politica_no_permitida",
            revoked_by="policy",
        )
        changed = True
    return {
        "reconciled": True,
        "node": node_domain,
        "policy_allowed": policy_allowed,
        "allowed": bool(node.allowed),
        "changed": changed,
    }


@router.get("/heartbeat", deprecated=True)
async def federation_heartbeat():
    return {"alive": True}


async def get_current_federation_peer(request: Request) -> dict | None:
    """Valida un Bearer token de federación entrante contra la clave pública JWKS del emisor.

    Extrae el ``iss`` del token sin verificar (para saber qué nodo lo firmó) y
    valida la firma contra el JWKS de ese nodo. Retorna el payload o None.
    """
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:].strip()
    if not token:
        return None
    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
    except jwt.PyJWTError:
        return None
    issuer = unverified.get("iss")
    if not issuer:
        return None
    try:
        jwks = await _fetch_peer_jwks(issuer)
    except Exception:
        return None
    keys = jwks.get("keys", [])
    if not keys:
        return None
    key = keys[0]
    n = int.from_bytes(base64.urlsafe_b64decode(key["n"] + "=="), "big")
    e = int.from_bytes(base64.urlsafe_b64decode(key["e"] + "=="), "big")
    public_numbers = RSAPublicNumbers(e, n)
    public_key = public_numbers.public_key()
    public_pem = public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode("ascii")
    try:
        payload = jwt.decode(
            token,
            public_pem,
            algorithms=["RS256"],
            audience="clakettes-federation",
            issuer=issuer,
            options={"require": ["exp", "iss", "aud", "sub", "typ"]},
        )
        if payload.get("typ") != "federation":
            return None
        return payload
    except jwt.PyJWTError:
        return None


@router.get("/whoami")
async def federation_whoami(peer: dict | None = Depends(get_current_federation_peer)):
    if peer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Federation peer identity required",
        )
    return {
        "node": peer.get("issuer_node") or peer.get("iss"),
        "issuer": peer.get("iss"),
        "subject": peer.get("sub"),
    }


@router.get("/peers", deprecated=True)
async def federation_peers():
    return {"peers": []}


@router.get("/links", deprecated=True)
async def federation_links():
    return {"links": []}


@router.get("/stats", deprecated=True)
async def federation_stats():
    return {"stats": {}}


@router.get("/config", deprecated=True)
async def federation_config():
    return {"config": {}}


@router.get("/status-check", deprecated=True)
async def federation_status_check():
    return {"ok": True}


@router.get("/ready", deprecated=True)
async def federation_ready():
    return {"ready": True}


@router.get("/live", deprecated=True)
async def federation_live():
    return {"live": True}


@router.get("/alive", deprecated=True)
async def federation_alive():
    return {"alive": True}


@router.get("/down", deprecated=True)
async def federation_down():
    return {"down": False}


@router.get("/maintenance", deprecated=True)
async def federation_maintenance():
    return {"maintenance": False}


@router.get("/readyz", deprecated=True)
async def federation_readyz():
    return {"ready": True}


@router.get("/livez", deprecated=True)
async def federation_livez():
    return {"live": True}


@router.get("/healthz", deprecated=True)
async def federation_healthz():
    return {"healthy": True}


@router.get("/ok", deprecated=True)
async def federation_ok():
    return {"ok": True}


@router.get("/yes", deprecated=True)
async def federation_yes():
    return {"yes": True}


@router.get("/no", deprecated=True)
async def federation_no():
    return {"no": False}


@router.get("/maybe", deprecated=True)
async def federation_maybe():
    return {"maybe": True}


@router.get("/always", deprecated=True)
async def federation_always():
    return {"always": True}


@router.get("/never", deprecated=True)
async def federation_never():
    return {"never": False}


@router.post("/import")
async def federation_import(payload: dict, request: Request, db: Session = Depends(get_db)):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bundle must be an object")
    origin = payload.get("origin_domain")
    if not isinstance(origin, str) or not origin.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bundle.origin_domain required")
    await _resolve_peer_node(request, origin)
    try:
        return portability_service.import_bundle(db, payload)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid bundle: integrity check failed")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Origin node not allowed")


@router.post("/dedup")
async def federation_dedup(payload: dict, request: Request, db: Session = Depends(get_db)):
    claimed = payload.get("node") or payload.get("node_origin") if isinstance(payload, dict) else None
    node_domain = await _resolve_peer_node(request, claimed)
    message_ids = payload.get("message_ids") if isinstance(payload, dict) else None
    if message_ids is None:
        message_ids = [payload.get("message_id")] if isinstance(payload, dict) else []
    if (
        not isinstance(message_ids, list)
        or not message_ids
        or not all(isinstance(mid, str) and mid.strip() for mid in message_ids)
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="message_id or message_ids required")
    queue = federation_chat_bridge.queue
    results = [{"message_id": mid, "duplicate": queue.get_by_message_id(db, mid) is not None} for mid in message_ids]
    return {
        "deduped": True,
        "node": node_domain,
        "results": results,
        "duplicates": sum(1 for item in results if item["duplicate"]),
    }


@router.post("/retry")
async def federation_retry(payload: dict, request: Request):
    claimed = payload.get("node") or payload.get("node_domain") if isinstance(payload, dict) else None
    node_domain = await _resolve_peer_node(request, claimed)
    retries = [item for item in event_bus.list_retries() if item.get("node_domain") == node_domain]
    due = [item for item in event_bus.due_retries() if item.get("node_domain") == node_domain]
    if retries:
        federation_events_router._ensure_worker()
    return {
        "retried": True,
        "node": node_domain,
        "pending": retries,
        "count": len(retries),
        "due": len(due),
        "worker_started": bool(retries),
    }


@router.post("/recover-node")
async def federation_recover_node(payload: dict, request: Request, db: Session = Depends(get_db)):
    claimed = payload.get("node") or payload.get("node_domain") if isinstance(payload, dict) else None
    node_domain = await _resolve_peer_node(request, claimed)
    result = await _recover_federation_node(node_domain, db)
    if isinstance(result, JSONResponse):
        return result
    return {**result, "recovered": True}


@router.get("/integrity")
async def federation_integrity(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    nodes = db.query(TrustedNode).all()
    expired_certificates = [
        node.node_domain
        for node in nodes
        if node.not_after is not None and _utc_naive(node.not_after) < _utc_naive(now)
    ]
    invalid_fingerprints = [
        node.node_domain for node in nodes if not re.fullmatch(r"[0-9a-fA-F]{64}", node.cert_fingerprint_sha256 or "")
    ]
    manifest_issues = []
    manifest = await federation_manifest()
    signature = manifest.get("signature")
    if not manifest.get("schema_version") or not signature:
        manifest_issues.append("manifest_incompleto")
    else:
        try:
            if datetime.fromisoformat(manifest["expires_at"]) < now:
                manifest_issues.append("manifest_expirado")
        except (KeyError, TypeError, ValueError):
            manifest_issues.append("manifest_expirado_invalido")
        try:
            payload = _canonical_json(_manifest_signature_payload(manifest))
            _signing_key().public_key().verify(
                base64.b64decode(signature), payload, padding.PKCS1v15(), hashes.SHA256()
            )
        except Exception:
            manifest_issues.append("manifest_firma_invalida")
    issues = {
        "expired_certificates": expired_certificates,
        "invalid_fingerprints": invalid_fingerprints,
        "manifest_issues": manifest_issues,
    }
    return {
        "integrity": not any(issues.values()),
        "nodes": len(nodes),
        **issues,
        "checked_at": now.isoformat(),
    }


@router.get("/metrics")
async def federation_metrics():
    return federation_resilience.metrics.snapshot()


@router.get("/users/{ref}")
async def resolve_user(ref: str, request: Request, db: Session = Depends(get_db)):
    _require_peer(request)
    user = db.query(User).filter((User.uuid == ref) | (User.did == ref) | (User.handle == ref)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "uuid": user.uuid, "did": user.did, "handle": user.handle, "username": user.username}


@router.get("/.well-known/webfinger")
async def webfinger(resource: str, request: Request, db: Session = Depends(get_db)):
    _require_peer(request)
    # resource like acct:user@domain
    handle = resource.split("acct:")[-1]
    user = db.query(User).filter((User.handle == handle) | (User.username == handle.split("@")[0])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"subject": resource, "links": [{"rel": "self", "href": f"/api/users/{user.id}"}]}


class PeerVerifyIn(BaseModel):
    node_domain: str
    certificate_chain: list[str]  # PEM certificados, primero el del nodo
    manifest_signature: str | None = None
    manifest_payload: dict | None = None


@router.post("/peers/verify")
async def peers_verify(body: PeerVerifyIn, db: Session = Depends(get_db)):
    """Valida la identidad de un nodo remoto: dominio + certificado + manifiesto firmado.

    Devuelve si el nodo es de confianza y su huella de certificado.
    """
    service = NodePeeringService()
    if not body.certificate_chain:
        raise HTTPException(status_code=400, detail="certificate_chain required")

    cert_pem = body.certificate_chain[0]
    from app.mtls import cert_fingerprint_sha256

    fingerprint = cert_fingerprint_sha256(cert_pem)

    # El dominio del manifiesto/cert debe coincidir con node_domain
    node = service.get_by_domain(db, body.node_domain)
    if node is None:
        return {"trusted": False, "reason": "dominio_no_registrado", "fingerprint": fingerprint}
    if node.cert_fingerprint_sha256 != fingerprint:
        return {"trusted": False, "reason": "huella_cert_no_coincide", "fingerprint": fingerprint}
    if not node.allowed:
        return {"trusted": False, "reason": "nodo_no_autorizado", "fingerprint": fingerprint}
    if body.manifest_signature is not None and body.manifest_payload is not None:
        try:
            cert = x509.load_pem_x509_certificate(cert_pem.encode("ascii"))
            signature = base64.b64decode(body.manifest_signature)
            canonical = _canonical_json(_manifest_signature_payload(body.manifest_payload))
            cert.public_key().verify(signature, canonical, padding.PKCS1v15(), hashes.SHA256())
        except Exception:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="manifest_signature_invalid")
    return {"trusted": True, "domain": body.node_domain, "fingerprint": fingerprint}


@router.post("/peers/{domain}/revoke")
async def peers_revoke(domain: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require_admin(current_user)
    service = NodePeeringService()
    ok = service.revoke(db, domain)
    if not ok:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    federation_resilience.record_revocation(db, domain, revoked_by=str(current_user.id))
    return {"domain": domain, "revoked": True}


@router.get("/.well-known/jwks.json")
async def federation_jwks():
    """Clave pública de federación en formato JWKS para validación de tokens de pares."""
    return federation_token_service.jwks()


class FederationTokenIn(BaseModel):
    subject: str


@router.post("/token")
async def federation_issue_token(body: FederationTokenIn, request: Request, db: Session = Depends(get_db)):
    """Emite un JWT de federación firmado (RS256). Requiere peer mTLS verificado."""
    peer = _require_peer(request)
    if peer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="mTLS peer identity required",
        )
    token = federation_token_service.create_token(
        body.subject,
        extra_claims={"issuer_node": peer.node_domain},
    )
    return {"access_token": token, "token_type": "Bearer", "expires_in": federation_token_service.ttl_seconds}
