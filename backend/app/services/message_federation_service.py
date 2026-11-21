import base64
from typing import Any

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from sqlalchemy.orm import Session

from app.models.node_policy import NodePolicy
from app.services.federation_token_service import FederationTokenService
from app.services.node_peering_service import NodePeeringService
from app.services.message_queue_service import canonical_json

SIGNED_FIELDS = ("message_id", "node_origin", "channel_id", "receiver_id", "content", "timestamp")


class MessageFederationService:
    def __init__(
        self,
        token_service: FederationTokenService | None = None,
        fetcher: Any = None,
    ) -> None:
        self._tokens = token_service or FederationTokenService()
        self.fetch_peer_public_key_pem = fetcher or self._default_fetcher

    def sign(self, fields: dict[str, Any]) -> str:
        key = serialization.load_pem_private_key(self._tokens.private_pem().encode("ascii"), password=None)
        payload = {k: fields.get(k) for k in SIGNED_FIELDS}
        signature = key.sign(canonical_json(payload), padding.PKCS1v15(), hashes.SHA256())
        return base64.b64encode(signature).decode("ascii")

    def verify(self, envelope: dict[str, Any], public_pem: str) -> bool:
        try:
            key = serialization.load_pem_public_key(public_pem.encode("ascii"))
            payload = {k: envelope.get(k) for k in SIGNED_FIELDS}
            key.verify(
                base64.b64decode(envelope.get("signature", "")),
                canonical_json(payload),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    async def _default_fetcher(self, node_origin: str) -> str | None:
        url = f"https://{node_origin}/api/federation/.well-known/jwks.json"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5)
                response.raise_for_status()
                keys = response.json().get("keys", [])
        except Exception:
            return None
        if not keys:
            return None
        return self._pem_from_jwk(keys[0])

    @staticmethod
    def _pem_from_jwk(jwk: dict[str, Any]) -> str | None:
        try:
            n = int.from_bytes(base64.urlsafe_b64decode(jwk["n"] + "=="), "big")
            e = int.from_bytes(base64.urlsafe_b64decode(jwk["e"] + "=="), "big")
        except Exception:
            return None
        key = RSAPublicNumbers(e, n).public_key()
        return key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode("ascii")

    def is_node_permitted(self, db: Session, node_origin: str) -> bool:
        policy = db.query(NodePolicy).filter(NodePolicy.node_domain == node_origin).first()
        if policy is not None and (not policy.allowed or policy.disable_chat):
            return False
        node = NodePeeringService().get_by_domain(db, node_origin)
        if node is not None and not node.allowed:
            return False
        return True

    def local_node(self) -> str:
        return self._tokens.issuer


message_federation_service = MessageFederationService()
