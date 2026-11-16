# Seguridad federada (Fase 2 y 3)

## Modelo de confianza

- Identidad de nodo = dominio + certificado TLS X.509.
- Peering mutuo vía mTLS con certificados de dominio (CA pública o privada).
- TLS obligatorio entre nodos; validación estricta de certificados en peering (sin self-signed en prod).
- La identidad se almacena en `trusted_nodes` (dominio, huella SHA-256 del certificado, CA emisora, vigencia, políticas).
- Cada nodo expone un manifiesto firmado con la clave privada de su certificado TLS; los pares validan la firma contra el certificado del nodo.

## Rotación y revocación

- La rotación se gestiona por renovación del certificado: al renovarse, se actualiza la huella en `trusted_nodes` sin romper el peering (la raíz de confianza es la CA, no el cert individual).
- Un nodo comprometido se revoca marcando `allowed = false` en `trusted_nodes` (`POST /api/federation/peers/{domain}/revoke`, solo admin) o invalidando su certificado en la CRL de la CA.
- La revocación administrativa es inmediata: el siguiente handshake mTLS falla.

## Controles de acceso

- Rate limiting global: 100 req/60s por IP (bucket `middleware:`); `/dav` tiene 600/60s.
- Rate limiting por endpoint sensible: login 5/300s por IP, refresh 20/60s por IP, federation 60/60s por IP.
- Endpoints de federación que exponen datos de usuario (`/users/{ref}`, `/.well-known/webfinger`) requieren peer mTLS verificado.
- Endpoints de administración de nodos (`/nodes`, `/peers/{domain}/revoke`) requieren rol admin.

## Ajustes

- `allowlist`/`blocklist` por nodo (`node_policies` / `trusted_nodes`).
- Rate limiting y anti-flood en el borde de federación.
- Propagación de reportes de moderación entre nodos.
- `consent_required`: exige consentimiento explícito antes de federar datos de un nodo.
- `import_only`: federación unidireccional (solo importar, no exportar).
- `disable_chat`/`disable_search`: permisos por función por nodo.
- `minimize_data`: no compartir más de lo necesario en peering.

## Referencias

- `docs/es/MODELO_CONFIANZA_NODOS.md` — diseño detallado del modelo de confianza y tablas de base de datos.
- `docs/es/FEDERATION_PROTOCOL.md` — pasos de interoperabilidad nodo-servidor/cliente.
- `docs/es/FEDERATION_SCHEMA.md` — Clakettes Schema v1 y endpoints de federación.
- `docs/es/AMENAZAS_NODOS_FEDERACION.md` — amenazas por nodo y riesgos residuales.
