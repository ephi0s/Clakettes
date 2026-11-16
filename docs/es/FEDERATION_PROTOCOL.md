# Protocolo de federación Clakettes (Fase 4)

Pasos para crear un servidor/cliente interoperable:

1. Implementar los endpoints `/api/federation/*` (ver `docs/es/FEDERATION_SCHEMA.md`).
2. Configurar TLS obligatorio entre nodos con mTLS mutuo (Fase 2): certificado emitido por una CA de confianza, sin self-signed en producción.
3. Registrar el nodo como confiado en cada par con el que hará peering (`trusted_nodes`: dominio, huella SHA-256 del certificado, capacidades, políticas).
4. Exponer el manifiesto en `GET /api/federation/manifest` con `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` y `certificate_chain`. El manifiesto se firma con la clave privada del certificado TLS del nodo.
5. Exponer la clave pública en `GET /api/federation/.well-known/jwks.json` para que los pares validen los tokens de federación.
6. Validar tokens de pares vía JWKS: un nodo remoto que llama a un endpoint protegido debe presentar un Bearer JWT firmado (RS256) cuyo `iss` sea su dominio y cuya firma se valide contra su JWKS.
7. Resolver usuarios remotos vía `GET /api/federation/users/{ref}` y `GET /api/federation/.well-known/webfinger` (ambos requieren peer mTLS verificado).
8. Usar Clakettes Schema v1 para el intercambio de datos.

## Motivación

El protocolo permite que nodos independientes intercambien festivales, usuarios y mensajes sin perder identidad ni trazabilidad.

## Ajustes

- `consent_required`: exige consentimiento explícito antes de federar datos de un nodo.
- `import_only`: federación unidireccional (solo importar, no exportar).
- `disable_chat`/`disable_search`: permisos por función por nodo.
- `minimize_data`: no compartir más de lo necesario en peering.

## Endpoints clave

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/federation/manifest` | GET | Manifiesto firmado del nodo |
| `/api/federation/directory` | GET | Directorio de nodos confiados |
| `/api/federation/nodes` | GET/POST | Políticas de allowlist/blocklist |
| `/api/federation/.well-known/jwks.json` | GET | Clave pública JWKS del nodo |
| `/api/federation/token` | POST | Emisión de JWT de federación (RS256) |
| `/api/federation/peers/verify` | POST | Verificación de identidad de nodo remoto |
| `/api/federation/peers/{domain}/revoke` | POST | Revocación de nodo confiado (admin) |
| `/api/federation/users/{ref}` | GET | Resolución de usuario remoto (mTLS) |
| `/api/federation/.well-known/webfinger` | GET | WebFinger `acct:user@domain` (mTLS) |
| `/api/federation/reports` | POST/GET/PATCH | Reportes de moderación entre nodos |
