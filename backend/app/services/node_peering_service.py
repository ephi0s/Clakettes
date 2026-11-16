"""Servicio de peering federado mTLS (Fase 2).

Gestiona el almacén de nodos confiados, la validación de identidad (dominio +
certificado TLS), la rotación por renovación de certificado y la revocación.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.trusted_node import TrustedNode, NodePeeringSession


class NodePeeringService:
    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Registro y consulta de nodos confiados
    # ------------------------------------------------------------------

    def get_by_domain(self, db: Session, node_domain: str) -> TrustedNode | None:
        return db.query(TrustedNode).filter(TrustedNode.node_domain == node_domain).first()

    def get_by_fingerprint(self, db: Session, fingerprint_sha256: str) -> TrustedNode | None:
        return db.query(TrustedNode).filter(TrustedNode.cert_fingerprint_sha256 == fingerprint_sha256).first()

    def list_allowed(self, db: Session) -> list[TrustedNode]:
        return db.query(TrustedNode).filter(TrustedNode.allowed.is_(True)).all()

    # ------------------------------------------------------------------
    # Alta / actualización de un nodo confiado (tras handshake mTLS exitoso)
    # ------------------------------------------------------------------

    def register_or_update(
        self,
        db: Session,
        node_domain: str,
        fingerprint_sha256: str,
        subject_cn: str | None = None,
        sans: list[str] | None = None,
        issuer_ca: str | None = None,
        not_before: datetime | None = None,
        not_after: datetime | None = None,
        capabilities: list[str] | None = None,
        allowed: bool = True,
    ) -> TrustedNode:
        """Crea o actualiza un nodo confiado a partir de los datos del cert TLS.

        Se identifica por dominio. Si el certificado cambió (rotación), se
        actualiza la huella y las fechas de vigencia sin romper el peering.
        """
        node = self.get_by_domain(db, node_domain)
        now = datetime.now(timezone.utc)
        if node is None:
            node = TrustedNode(
                node_domain=node_domain,
                cert_fingerprint_sha256=fingerprint_sha256,
                cert_subject_cn=subject_cn,
                cert_sans=sans,
                issuer_ca=issuer_ca,
                not_before=not_before,
                not_after=not_after,
                capabilities=capabilities,
                allowed=allowed,
                last_seen_at=now,
            )
            db.add(node)
        else:
            node.cert_fingerprint_sha256 = fingerprint_sha256
            node.cert_subject_cn = subject_cn
            node.cert_sans = sans
            node.issuer_ca = issuer_ca
            node.not_before = not_before
            node.not_after = not_after
            node.capabilities = capabilities
            node.allowed = allowed
            node.last_seen_at = now
        db.commit()
        db.refresh(node)
        return node

    # ------------------------------------------------------------------
    # Validación de identidad de un nodo remoto durante peering mTLS
    # ------------------------------------------------------------------

    def validate_peer_identity(
        self,
        db: Session,
        node_domain: str,
        fingerprint_sha256: str,
        remote_ip: str | None = None,
    ) -> tuple[bool, str | None, TrustedNode | None]:
        """Devuelve (valido, motivo_rechazo_o_None, nodo_o_None).

        Reglas:
        1. El dominio debe existir en trusted_nodes.
        2. La huella del cert presentado debe coincidir con la registrada.
        3. El nodo debe tener allowed = true.
        4. El cert no debe estar expirado (not_after > ahora).
        """
        node = self.get_by_domain(db, node_domain)
        if node is None:
            self._log_session(db, None, node_domain, remote_ip, fingerprint_sha256, False, "dominio_no_registrado")
            return False, "dominio_no_registrado", None

        if node.cert_fingerprint_sha256 != fingerprint_sha256:
            self._log_session(db, node.id, node_domain, remote_ip, fingerprint_sha256, False, "huella_cert_no_coincide")
            return False, "huella_cert_no_coincide", node

        if not node.allowed:
            self._log_session(db, node.id, node_domain, remote_ip, fingerprint_sha256, False, "nodo_no_autorizado")
            return False, "nodo_no_autorizado", node

        if node.not_after is not None and node.not_after < datetime.now(timezone.utc):
            self._log_session(db, node.id, node_domain, remote_ip, fingerprint_sha256, False, "cert_expirado")
            return False, "cert_expirado", node

        node.last_seen_at = datetime.now(timezone.utc)
        db.commit()
        self._log_session(db, node.id, node_domain, remote_ip, fingerprint_sha256, True, None)
        return True, None, node

    # ------------------------------------------------------------------
    # Revocación
    # ------------------------------------------------------------------

    def revoke(self, db: Session, node_domain: str, reason: str | None = None) -> bool:
        """Marca un nodo como no permitido (revocación administrativa inmediata)."""
        node = self.get_by_domain(db, node_domain)
        if node is None:
            return False
        node.allowed = False
        db.commit()
        return True

    def restore(self, db: Session, node_domain: str) -> bool:
        """Vuelve a permitir un nodo previamente revocado."""
        node = self.get_by_domain(db, node_domain)
        if node is None:
            return False
        node.allowed = True
        db.commit()
        return True

    # ------------------------------------------------------------------
    # Rotación por renovación de certificado
    # ------------------------------------------------------------------

    def rotate_certificate(
        self,
        db: Session,
        node_domain: str,
        new_fingerprint_sha256: str,
        subject_cn: str | None = None,
        sans: list[str] | None = None,
        issuer_ca: str | None = None,
        not_before: datetime | None = None,
        not_after: datetime | None = None,
        capabilities: list[str] | None = None,
    ) -> TrustedNode | None:
        """Actualiza la huella y vigencia de un nodo tras renovar su cert TLS.

        El dominio se mantiene: la raíz de confianza es la CA, no el cert.
        """
        node = self.get_by_domain(db, node_domain)
        if node is None:
            return None
        node.cert_fingerprint_sha256 = new_fingerprint_sha256
        node.cert_subject_cn = subject_cn
        node.cert_sans = sans
        node.issuer_ca = issuer_ca
        node.not_before = not_before
        node.not_after = not_after
        node.capabilities = capabilities
        db.commit()
        db.refresh(node)
        return node

    # ------------------------------------------------------------------
    # Auditoría de sesiones de peering
    # ------------------------------------------------------------------

    def _log_session(
        self,
        db: Session,
        node_id: int | None,
        remote_domain: str | None,
        remote_ip: str | None,
        cert_fingerprint: str | None,
        validated: bool,
        reason: str | None,
    ) -> None:
        session = NodePeeringSession(
            node_id=node_id,
            remote_domain=remote_domain,
            remote_ip=remote_ip,
            cert_fingerprint=cert_fingerprint,
            validated=validated,
            reason=reason,
        )
        db.add(session)
        db.commit()
