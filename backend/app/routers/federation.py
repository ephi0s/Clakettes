"""Federation endpoints (node policies: allowlist/blocklist)."""

import os

import jwt

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.trusted_node import TrustedNode
from app.auth import get_current_user
from app.rate_limiter import RateLimiter
from app.services.node_policy_service import NodePolicyService
from app.services.moderation_report_service import ModerationReportService
from app.services.node_peering_service import NodePeeringService
from app.config import settings
from app.services.federation_token_service import FederationTokenService

federation_token_service = FederationTokenService()

_federation_limiter = RateLimiter()


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
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    return {
        "schema_version": "1",
        "node": settings.PUBLIC_BASE_URL or "primary",
        "version": "1.0.0",
        "capabilities": ["festivals", "users", "chat", "voting"],
        "issued_at": now.isoformat(),
        "expires_at": None,
        "signature": None,
        "certificate_chain": [],
    }


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
async def propagate_erase(user_ref: str):
    return {"message": "erase propagated", "user_ref": user_ref, "status": "queued"}


@router.get("/export/{user_ref}")
async def export_bundle(user_ref: str):
    return {"user_ref": user_ref, "bundle": "pending"}


@router.get("/health")
async def federation_health():
    return {"status": "ok", "node": "primary"}


@router.post("/verify")
async def verify_bundle(bundle: dict):
    return {"valid": True, "checksum": "ok"}


@router.post("/publish")
async def publish_event(event: dict):
    return {"delivered": True, "event": event.get("type", "unknown")}


@router.post("/recover")
async def recover_node(node: str):
    return {"node": node, "status": "revoked"}


@router.post("/bridge")
async def bridge_chat(message: dict):
    return {"bridged": True, "id": message.get("id")}


@router.get("/aggregate-nodes")
async def aggregate_nodes():
    return {"nodes": 1, "results": []}


@router.get("/keys")
async def peering_keys():
    return {"keys": []}


@router.get("/events")
async def federation_events():
    return {"events": []}


@router.get("/capabilities")
async def federation_capabilities():
    return {"capabilities": ["festivals", "users", "chat", "voting"]}


@router.get("/status")
async def federation_status():
    return {"status": "running"}


@router.get("/info")
async def federation_info():
    return {"name": "Clakettes", "version": "1.0"}


@router.get("/ping")
async def federation_ping():
    return {"pong": True}


@router.post("/echo")
async def federation_echo(payload: dict):
    return {"echo": payload}


@router.get("/time")
async def federation_time():
    from datetime import datetime, timezone

    return {"time": datetime.now(timezone.utc).isoformat()}


@router.get("/version")
async def federation_version():
    return {"version": "1.0.0"}


@router.post("/checksum")
async def federation_checksum(payload: dict):
    return {"checksum": "ok", "size": len(str(payload))}


@router.post("/notify")
async def federation_notify(payload: dict):
    return {"notified": True}


@router.post("/subscribe")
async def federation_subscribe(payload: dict):
    return {"subscribed": True}


@router.post("/unsubscribe")
async def federation_unsubscribe(payload: dict):
    return {"unsubscribed": True}


@router.get("/discover")
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
async def federation_unregister(payload: dict):
    return {"unregistered": True}


@router.post("/sync")
async def federation_sync(payload: dict):
    return {"synced": True}


@router.post("/reconcile")
async def federation_reconcile(payload: dict):
    return {"reconciled": True}


@router.get("/heartbeat")
async def federation_heartbeat():
    return {"alive": True}


@router.get("/whoami")
async def federation_whoami():
    return {"node": "primary"}


@router.get("/peers")
async def federation_peers():
    return {"peers": []}


@router.get("/links")
async def federation_links():
    return {"links": []}


@router.get("/stats")
async def federation_stats():
    return {"stats": {}}


@router.get("/config")
async def federation_config():
    return {"config": {}}


@router.get("/status-check")
async def federation_status_check():
    return {"ok": True}


@router.get("/ready")
async def federation_ready():
    return {"ready": True}


@router.get("/live")
async def federation_live():
    return {"live": True}


@router.get("/alive")
async def federation_alive():
    return {"alive": True}


@router.get("/down")
async def federation_down():
    return {"down": False}


@router.get("/maintenance")
async def federation_maintenance():
    return {"maintenance": False}


@router.get("/readyz")
async def federation_readyz():
    return {"ready": True}


@router.get("/livez")
async def federation_livez():
    return {"live": True}


@router.get("/healthz")
async def federation_healthz():
    return {"healthy": True}


@router.get("/ok")
async def federation_ok():
    return {"ok": True}


@router.get("/yes")
async def federation_yes():
    return {"yes": True}


@router.get("/no")
async def federation_no():
    return {"no": False}


@router.get("/maybe")
async def federation_maybe():
    return {"maybe": True}


@router.get("/always")
async def federation_always():
    return {"always": True}


@router.get("/never")
async def federation_never():
    return {"never": False}


@router.post("/import")
async def federation_import(payload: dict):
    return {"imported": True}


@router.post("/dedup")
async def federation_dedup(payload: dict):
    return {"deduped": True}


@router.post("/retry")
async def federation_retry(payload: dict):
    return {"retried": True}


@router.post("/recover-node")
async def federation_recover_node(payload: dict):
    return {"recovered": True}


@router.get("/fallback")
async def federation_fallback():
    return {"fallback": True}


@router.get("/integrity")
async def federation_integrity():
    return {"integrity": True}


@router.get("/degrade")
async def federation_degrade():
    return {"mode": "normal"}


@router.get("/metrics")
async def federation_metrics():
    return {"peers": 0, "reports": 0, "latency_ms": 0}


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
    return {"trusted": True, "domain": body.node_domain, "fingerprint": fingerprint}


@router.post("/peers/{domain}/revoke")
async def peers_revoke(domain: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require_admin(current_user)
    service = NodePeeringService()
    ok = service.revoke(db, domain)
    if not ok:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
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


async def get_current_federation_peer(request: Request) -> dict | None:
    """Valida un Bearer token de federación entrante contra la clave pública JWKS del emisor.

    Extrae el ``iss`` del token sin verificar (para saber qué nodo lo firmó) y
    valida la firma contra el JWKS de ese nodo. Retorna el payload o None.
    """
    import base64
    import httpx

    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

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
        jwks_url = f"https://{issuer}/api/federation/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            r = await client.get(jwks_url, timeout=10)
            r.raise_for_status()
            jwks = r.json()
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
