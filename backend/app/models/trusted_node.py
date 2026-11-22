"""Modelos de nodos confiados y sesiones de peering mTLS (Fase 2)."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Index
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class TrustedNode(BaseModel):
    """Nodo federado de confianza. Identidad = dominio + certificado TLS X.509.

    La raíz de confianza es la CA emisora del certificado, no el certificado
    individual: al renovarse el certificado (misma CA) se actualiza la huella
    y el peering se mantiene sin reconfiguración manual.
    """

    __tablename__ = "trusted_nodes"

    node_domain = Column(String(255), unique=True, nullable=False, index=True)
    cert_fingerprint_sha256 = Column(String(64), unique=True, nullable=False, index=True)
    cert_subject_cn = Column(String(255), nullable=True)
    cert_sans = Column(mysql.JSON, nullable=True)  # lista de dNSName
    issuer_ca = Column(String(255), nullable=True)
    not_before = Column(DateTime, nullable=True)
    not_after = Column(DateTime, nullable=True)
    allowed = Column(Boolean, default=True, nullable=False)
    consent_required = Column(Boolean, default=True, nullable=False)
    minimize_data = Column(Boolean, default=True, nullable=False)
    capabilities = Column(mysql.JSON, nullable=True)  # lista de capacidades del manifiesto
    last_seen_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    revocation_reason = Column(Text, nullable=True)
    revoked_by = Column(String(255), nullable=True)

    peering_sessions = relationship(
        "NodePeeringSession",
        back_populates="node",
        cascade="all, delete-orphan",
    )


class NodePeeringSession(BaseModel):
    """Auditoría de handshakes mTLS intentados contra este nodo."""

    __tablename__ = "node_peering_sessions"

    node_id = Column(Integer, ForeignKey("trusted_nodes.id"), nullable=False, index=True)
    remote_domain = Column(String(255), nullable=True)
    remote_ip = Column(String(45), nullable=True)
    cert_fingerprint = Column(String(64), nullable=True)
    validated = Column(Boolean, default=False, nullable=False)
    reason = Column(Text, nullable=True)

    node = relationship("TrustedNode", back_populates="peering_sessions")


Index("ix_trusted_nodes_domain_allowed", TrustedNode.node_domain, TrustedNode.allowed)
