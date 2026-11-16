"""Modelos de datos del Clakettes Schema v1 para federación."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class Festival(BaseModel):
    """Festival intercambiable entre nodos."""

    id: str
    name: str
    edition: str | None = None
    created_at: datetime
    owner_node: str


class User(BaseModel):
    """Usuario federado."""

    id: str
    uuid: str | None = None
    did: str | None = None
    handle: str | None = None
    username: str
    node_origin: str


class Message(BaseModel):
    """Mensaje de chat federado."""

    id: str
    sender: str
    recipient: str | None = None
    body: str
    created_at: datetime
    node_origin: str


class ModerationReport(BaseModel):
    """Reporte de moderación entre nodos."""

    id: str | None = None
    reporter_node: str
    target_node: str
    target_user_ref: str | None = None
    reason: str
    status: str = "pending"


class Manifest(BaseModel):
    """Manifiesto firmado de un nodo federado."""

    schema_version: str = "1"
    node: str
    version: str = "1.0.0"
    capabilities: list[str] = Field(default_factory=list)
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    signature: str | None = None
    certificate_chain: list[str] = Field(default_factory=list)


class PeerInfo(BaseModel):
    """Información de un nodo confiado del directorio."""

    domain: str
    schema_version: str = "1"
    status: str = "unknown"
    version: str = "1.0.0"
    last_seen: str | None = None
    cert_fingerprint_sha256: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    consent_required: bool = True
    minimize_data: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PeerInfo":
        return cls(
            domain=data.get("domain", ""),
            schema_version=data.get("schema_version", "1"),
            status=data.get("status", "unknown"),
            version=data.get("version", "1.0.0"),
            last_seen=data.get("last_seen"),
            cert_fingerprint_sha256=data.get("cert_fingerprint_sha256"),
            capabilities=data.get("capabilities", []) or [],
            consent_required=data.get("consent_required", True),
            minimize_data=data.get("minimize_data", True),
        )


class TokenResponse(BaseModel):
    """Respuesta de emisión de token de federación."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600


class VerifyResponse(BaseModel):
    """Respuesta de verificación de identidad de par."""

    trusted: bool
    domain: str | None = None
    fingerprint: str | None = None
    reason: str | None = None


class WebFingerResponse(BaseModel):
    """Respuesta de WebFinger."""

    subject: str
    links: list[dict[str, Any]] = Field(default_factory=list)


class RevokeResponse(BaseModel):
    """Respuesta de revocación de par."""

    domain: str
    revoked: bool
