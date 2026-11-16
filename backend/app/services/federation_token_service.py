"""Servicio de tokens de federación entre nodos (Fase 3).

Genera un par de claves RSA para firmar JWTs de federación. La clave pública
se expone vía JWKS en ``GET /api/federation/.well-known/jwks.json`` para que
los nodos pares puedan validar los tokens emitidos por este nodo.

Los tokens de federación son JWT RS256 con claim ``iss`` = dominio del nodo
emisor y ``aud`` = ``clakettes-federation``.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.config import settings


class FederationTokenService:
    def __init__(
        self,
        private_key_pem: Optional[str] = None,
        public_key_pem: Optional[str] = None,
        issuer: Optional[str] = None,
        ttl_seconds: int = 3600,
    ):
        self.issuer = issuer or (settings.PUBLIC_BASE_URL or "clakettes")
        self.ttl_seconds = ttl_seconds
        self._private_key = self._load_or_generate_private_key(private_key_pem)
        self._public_key = self._private_key.public_key()
        self._public_pem = public_key_pem or self._public_key.public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode("ascii")

    def _load_or_generate_private_key(self, pem: Optional[str]):
        if pem:
            return serialization.load_pem_private_key(pem.encode("ascii"), password=None)
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def private_pem(self) -> str:
        return self._private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode("ascii")

    def public_pem(self) -> str:
        return self._public_pem

    def create_token(self, subject: str, extra_claims: dict | None = None) -> str:
        """Firma un JWT de federación RS256."""
        now = datetime.now(timezone.utc)
        payload = {
            "iss": self.issuer,
            "aud": "clakettes-federation",
            "sub": subject,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=self.ttl_seconds)).timestamp()),
            "typ": "federation",
        }
        if extra_claims:
            payload.update(extra_claims)
        return jwt.encode(payload, self.private_pem(), algorithm="RS256")

    def jwks(self) -> dict:
        """Devuelve la clave pública en formato JWKS."""
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

        self._public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        # Construye JWK RS256 mínimo (n, e) desde la clave pública
        pub_numbers = self._public_key.public_numbers()
        n = pub_numbers.n
        e = pub_numbers.e

        def int_to_b64url(val: int) -> str:
            import base64

            nbytes = (val.bit_length() + 7) // 8
            raw = val.to_bytes(nbytes, "big")
            return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

        return {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "kid": "federation-v1",
                    "alg": "RS256",
                    "n": int_to_b64url(n),
                    "e": int_to_b64url(e),
                }
            ]
        }

    def verify_token(self, token: str, issuer: str | None = None) -> dict | None:
        """Valida un JWT de federación RS256. Devuelve el payload o None."""
        try:
            payload = jwt.decode(
                token,
                self.public_pem(),
                algorithms=["RS256"],
                audience="clakettes-federation",
                issuer=issuer or self.issuer,
                options={"require": ["exp", "iss", "aud", "sub", "typ"]},
            )
            if payload.get("typ") != "federation":
                return None
            return payload
        except jwt.PyJWTError:
            return None
