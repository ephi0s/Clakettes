"""SDK ligero de federación Clakettes (Fase 4).

Modelos de datos del Schema v1 y cliente HTTP para consumir los endpoints
de federación de un nodo remoto.
"""

from app.sdk.models import (
    Festival,
    User,
    Message,
    ModerationReport,
    Manifest,
    PeerInfo,
    TokenResponse,
    VerifyResponse,
    WebFingerResponse,
    RevokeResponse,
)
from app.sdk.client import FederationClient

__all__ = [
    "Festival",
    "User",
    "Message",
    "ModerationReport",
    "Manifest",
    "PeerInfo",
    "TokenResponse",
    "VerifyResponse",
    "WebFingerResponse",
    "RevokeResponse",
    "FederationClient",
]
