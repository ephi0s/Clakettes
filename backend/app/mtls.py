"""Utilidades mTLS para peering federado (Fase 2).

Extrae la identidad del certificado TLS de cliente presentado durante el
handshake mTLS y la compara contra el almacén de nodos confiados.

NOTA: uvicorn/Starlette no exponen el certificado TLS del cliente directamente
en el scope ASGI. En producción el certificado se recibe en un reverse proxy
(nginx, Traefik, Caddy) que lo inyecta en headers (p. ej. X-SSL-Client-Cert,
X-SSL-Client-SHA256). Este middleware lee esos headers y falla cerrado si no
están presentes cuando se exige mTLS.
"""

from __future__ import annotations

import base64
import hashlib
from typing import Optional

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.services.node_peering_service import NodePeeringService
from app.database import SessionLocal


def _b64url_no_pad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def cert_fingerprint_sha256(cert_pem: str) -> str:
    """Huella SHA-256 de un certificado PEM (sin delimitadores, sin padding)."""
    der = base64.b64decode("".join(line for line in cert_pem.splitlines() if not line.startswith("-----")))
    return hashlib.sha256(der).hexdigest()


def _cert_subject_cn(cert_pem: str) -> Optional[str]:
    from cryptography import x509
    from cryptography.x509.oid import NameOID

    try:
        cert = x509.load_pem_x509_certificate(cert_pem.encode("ascii"))
        attrs = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    except Exception:
        return None
    return attrs[0].value if attrs else None


def extract_client_cert_info(request: Request) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Extrae (subject_cn, fingerprint_sha256, cert_pem) de los headers mTLS del proxy.

    Headers esperados (configurados en el reverse proxy):
    - X-SSL-Client-Cert: certificado PEM del cliente (una línea o multiline con \n)
    - X-SSL-Client-SHA256: huella SHA-256 opcional (si el proxy la expone)
    - X-SSL-Client-Subject-CN: CN opcional
    - X-Forwarded-For / X-Real-IP: IP remota

    El CN se usa como dominio del par. Si el proxy no expone la huella o el CN,
    ambos se recalculan a partir del PEM del certificado.
    Retorna (None, None, None) si no hay certificado de cliente.
    """
    cert_pem = request.headers.get("x-ssl-client-cert")
    if not cert_pem:
        return None, None, None

    fingerprint = request.headers.get("x-ssl-client-sha256")
    if not fingerprint:
        fingerprint = cert_fingerprint_sha256(cert_pem)

    subject_cn = request.headers.get("x-ssl-client-subject-cn")
    if not subject_cn:
        subject_cn = _cert_subject_cn(cert_pem)
    return subject_cn or None, fingerprint, cert_pem


class MTLSPeerVerificationMiddleware(BaseHTTPMiddleware):
    """Verifica la identidad de nodos remotos en endpoints de federación.

    Solo se aplica a rutas bajo /api/federation (salvo /health que se deja abierto).
    Si el encabezado de certificado de cliente falta, se rechaza con 401.
    Si la identidad no coincide con trusted_nodes, se rechaza con 403.
    """

    FEDERATION_PREFIX = "/api/federation"
    EXEMPT_PATHS = {"/api/federation/health", "/api/federation/ping", "/api/federation/status"}

    def __init__(self, app, require_mtls: bool = True):
        super().__init__(app)
        self.require_mtls = require_mtls

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not path.startswith(self.FEDERATION_PREFIX) or path in self.EXEMPT_PATHS:
            return await call_next(request)

        if not self.require_mtls:
            return await call_next(request)

        subject_cn, fingerprint, cert_pem = extract_client_cert_info(request)
        domain = subject_cn
        if domain is None or fingerprint is None:
            return Response(
                content='{"detail":"mTLS client certificate required"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json",
                headers={"WWW-Authenticate": 'mTLS realm="federation"'},
            )

        db = SessionLocal()
        try:
            valid, reason, node = NodePeeringService().validate_peer_identity(
                db, domain, fingerprint, request.client.host if request.client else None
            )
        finally:
            db.close()
        if not valid:
            return Response(
                content=f'{{"detail":"peer identity rejected: {reason}"}}',
                status_code=status.HTTP_403_FORBIDDEN,
                media_type="application/json",
            )

        # Exponer la identidad verificada para los endpoints de federación
        request.state.peer_node = node
        request.state.peer_domain = domain
        request.state.peer_fingerprint = fingerprint
        return await call_next(request)
