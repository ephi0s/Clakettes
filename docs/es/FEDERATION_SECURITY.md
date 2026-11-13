# Seguridad federada (Fase 2)

## Modelo de confianza

- Identidad de nodo = dominio + certificado TLS.
- Peering mutuo vía mTLS con certificados de dominio (CA pública o privada).
- TLS obligatorio entre nodos; validación estricta (sin self-signed en prod).

## Rotación y revocación

- La rotación/revocación se gestiona por renovación del certificado.
- Un nodo comprometido se revoca invalidando su certificado y su entrada en el directorio.

## Motivación

Evitar suplantación de nodos y garantizar que solo instancias verificadas participen en la federación.

## Ajustes

- `allowlist`/`blocklist` por nodo (`node_policies`).
- Rate limiting y anti-flood en el borde de federación.
- Propagación de reportes de moderación entre nodos.