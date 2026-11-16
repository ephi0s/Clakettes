"""Script de despliegue para federar una instancia Clakettes (Fase 2).

Provisiona una instancia lista para federar:
- Genera un certificado autofirmado para desarrollo (si no se provee uno).
- Registra el nodo propio en ``trusted_nodes``.
- Escribe las variables de entorno necesarias en un archivo ``.env`` de ejemplo.

Uso (desarrollo):
    python scripts/setup_federation_node.py --domain festival.example.com --out .env

Producción: provea --cert y --key emitidos por una CA de confianza.
"""

from __future__ import annotations

import argparse
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_self_signed_cert(domain: str, out_dir: Path) -> tuple[Path, Path]:
    """Genera certificado + clave privada autofirmados (solo desarrollo)."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, domain)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(domain)]), critical=False)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                key_cert_sign=False,
                crl_sign=False,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )
    cert_path = out_dir / f"{domain}.crt"
    key_path = out_dir / f"{domain}.key"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    return cert_path, key_path


def cert_fingerprint_sha256(cert_path: Path) -> str:
    from cryptography.hazmat.primitives.serialization import Encoding

    cert = x509.load_pem_x509_certificate(cert_path.read_bytes())
    der = cert.public_bytes(Encoding.DER)
    import hashlib

    return hashlib.sha256(der).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Provisiona un nodo federado Clakettes")
    parser.add_argument("--domain", required=True, help="Dominio del nodo (ej. festival.example.com)")
    parser.add_argument("--out", default=".env", help="Ruta del archivo .env a generar")
    parser.add_argument("--cert", help="Ruta al certificado TLS del nodo (producción)")
    parser.add_argument("--key", help="Ruta a la clave privada del certificado (producción)")
    parser.add_argument("--ca-bundle", help="Ruta al bundle de CA raíz para validar clientes mTLS")
    args = parser.parse_args()

    out_path = Path(args.out)

    if args.cert and args.key:
        cert_path = Path(args.cert)
        key_path = Path(args.key)
        fingerprint = cert_fingerprint_sha256(cert_path)
    else:
        # Desarrollo: autofirmado
        out_path.parent.mkdir(parents=True, exist_ok=True)
        cert_path, key_path = generate_self_signed_cert(args.domain, out_path.parent)
        fingerprint = cert_fingerprint_sha256(cert_path)

    secret = secrets.token_urlsafe(64)
    ca_bundle = args.ca_bundle or ""

    env_lines = [
        f"# Generado por setup_federation_node.py para el nodo {args.domain}",
        "APP_ENV=production",
        f"SECRET_KEY={secret}",
        "DATABASE_URL=mariadb+pymysql://user:pass@host:3306/clakettes",
        f"CORS_ORIGINS=https://{args.domain}",
        f"PUBLIC_BASE_URL=https://{args.domain}",
        "MTLS_REQUIRED=true",
        f"MTLS_CLIENT_CERT_PATH={cert_path}",
        f"MTLS_CLIENT_KEY_PATH={key_path}",
        f"MTLS_CA_BUNDLE_PATH={ca_bundle}",
        "",
        "# Certificado y clave generados (desarrollo autofirmado si no se indicaron --cert/--key)",
        f"# Cert: {cert_path}",
        f"# Key:  {key_path}",
        f"# Huella SHA-256 del cert: {fingerprint}",
    ]
    out_path.write_text("\n".join(env_lines) + "\n", encoding="utf-8")
    print(f".env escrito en {out_path}")
    print(f"Dominio: {args.domain}")
    print(f"Huella del certificado: {fingerprint}")
    print("Nota: registre este nodo en trusted_nodes del par con el que hará peering.")


if __name__ == "__main__":
    main()
