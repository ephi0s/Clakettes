"""Cliente HTTP de federación Clakettes (Fase 4).

Consume los endpoints de federación de un nodo remoto, con soporte mTLS
(certificado de cliente) y autenticación mediante token de federación (JWT
RS256 obtenido vía JWKS del nodo emisor).
"""

from __future__ import annotations

from typing import Any
import httpx

from app.sdk.models import (
    User,
    Manifest,
    PeerInfo,
    TokenResponse,
    VerifyResponse,
    WebFingerResponse,
    RevokeResponse,
)


class FederationClient:
    """Cliente para un nodo federado remoto.

    Args:
        base_url: URL base del nodo remoto (sin trailing slash, ej. https://festival.example.com/api).
        client_cert: ruta al certificado TLS de cliente para mTLS, o tupla (cert, key).
        client_key: ruta a la clave privada (si no va en client_cert).
        ca_bundle: ruta al bundle de CA raíz para validar el servidor remoto.
        timeout: segundos de timeout para peticiones HTTP.
    """

    def __init__(
        self,
        base_url: str,
        client_cert: str | None = None,
        client_key: str | None = None,
        ca_bundle: str | None = None,
        timeout: float = 10.0,
    ):
        self.base_url = base_url.rstrip("/")
        cert = None
        if client_cert:
            cert = (client_cert, client_key) if client_key else client_cert
        self._client = httpx.Client(
            cert=cert,
            verify=ca_bundle if ca_bundle else True,
            timeout=timeout,
        )
        self._access_token: str | None = None

    # ------------------------------------------------------------------
    # Autenticación de federación
    # ------------------------------------------------------------------

    def fetch_jwks(self) -> dict[str, Any]:
        """Descarga la clave pública JWKS del nodo remoto."""
        r = self._client.get(f"{self.base_url}/federation/.well-known/jwks.json")
        r.raise_for_status()
        return r.json()

    def issue_token(self, subject: str) -> TokenResponse:
        """Pide al nodo remoto un JWT de federación firmado (requiere mTLS)."""
        r = self._client.post(
            f"{self.base_url}/federation/token",
            json={"subject": subject},
        )
        r.raise_for_status()
        data = r.json()
        token_resp = TokenResponse(**data)
        self._access_token = token_resp.access_token
        return token_resp

    @property
    def access_token(self) -> str | None:
        return self._access_token

    def _headers(self, with_auth: bool = False) -> dict[str, str]:
        headers: dict[str, str] = {"Accept": "application/json"}
        if with_auth and self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers

    # ------------------------------------------------------------------
    # Identidad y directorio
    # ------------------------------------------------------------------

    def get_manifest(self) -> Manifest:
        r = self._client.get(f"{self.base_url}/federation/manifest", headers=self._headers())
        r.raise_for_status()
        return Manifest(**r.json())

    def get_directory(self) -> list[PeerInfo]:
        r = self._client.get(f"{self.base_url}/federation/directory", headers=self._headers())
        r.raise_for_status()
        return [PeerInfo.from_dict(n) for n in r.json().get("nodes", [])]

    def get_nodes(self) -> list[dict[str, Any]]:
        r = self._client.get(f"{self.base_url}/federation/nodes", headers=self._headers())
        r.raise_for_status()
        return r.json()

    # ------------------------------------------------------------------
    # Verificación y revocación de pares
    # ------------------------------------------------------------------

    def verify_peer(self, node_domain: str, certificate_chain: list[str]) -> VerifyResponse:
        """Valida la identidad de un nodo remoto (dominio + certificado + manifiesto)."""
        r = self._client.post(
            f"{self.base_url}/federation/peers/verify",
            json={
                "node_domain": node_domain,
                "certificate_chain": certificate_chain,
            },
            headers=self._headers(),
        )
        r.raise_for_status()
        return VerifyResponse(**r.json())

    def revoke_peer(self, domain: str) -> RevokeResponse:
        """Revocación administrativa de un nodo confiado (requiere admin)."""
        r = self._client.post(
            f"{self.base_url}/federation/peers/{domain}/revoke",
            headers=self._headers(with_auth=True),
        )
        r.raise_for_status()
        return RevokeResponse(**r.json())

    # ------------------------------------------------------------------
    # Usuarios y WebFinger
    # ------------------------------------------------------------------

    def resolve_user(self, ref: str) -> User:
        """Resuelve un usuario remoto por uuid, did o handle (requiere mTLS)."""
        r = self._client.get(
            f"{self.base_url}/federation/users/{ref}",
            headers=self._headers(),
        )
        r.raise_for_status()
        return User(**r.json())

    def webfinger(self, resource: str) -> WebFingerResponse:
        """Resuelve acct:user@domain vía WebFinger (requiere mTLS)."""
        r = self._client.get(
            f"{self.base_url}/federation/.well-known/webfinger",
            params={"resource": resource},
            headers=self._headers(),
        )
        r.raise_for_status()
        return WebFingerResponse(**r.json())

    # ------------------------------------------------------------------
    # Reportes de moderación
    # ------------------------------------------------------------------

    def create_report(
        self,
        reporter_node: str,
        target_node: str,
        reason: str,
        target_user_ref: str | None = None,
    ) -> dict[str, Any]:
        r = self._client.post(
            f"{self.base_url}/federation/reports",
            json={
                "reporter_node": reporter_node,
                "target_node": target_node,
                "target_user_ref": target_user_ref,
                "reason": reason,
            },
            headers=self._headers(with_auth=True),
        )
        r.raise_for_status()
        return r.json()

    def list_reports(self, node: str) -> list[dict[str, Any]]:
        r = self._client.get(
            f"{self.base_url}/federation/reports",
            params={"node": node},
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    def update_report_status(self, report_id: int, status: str) -> dict[str, Any]:
        r = self._client.patch(
            f"{self.base_url}/federation/reports/{report_id}",
            params={"status": status},
            headers=self._headers(with_auth=True),
        )
        r.raise_for_status()
        return r.json()

    # ------------------------------------------------------------------
    # Cierre
    # ------------------------------------------------------------------

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "FederationClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
