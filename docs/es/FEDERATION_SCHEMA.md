# Clakettes Schema v1

Versión inicial del schema de federación. Define las entidades mínimas intercambiables entre nodos, versionado mediante `schema_version` en el manifiesto de cada nodo.

## Modelo de confianza (Fase 2)

La identidad de un nodo es la tupla **(dominio, certificado TLS X.509)**. El peering entre nodos se realiza sobre mTLS mutuo: cada nodo valida la cadena de certificados del par contra su CA raíz, verifica que el dominio del cert coincida con el declarado, y rechaza certificados self-signed en producción. La rotación y revocación se gestionan por renovación de certificado.

## Entidades

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status

## Campos y restricciones

- `uuid`: identificador estable global (UUID v4).
- `did`: identificador descentralizado opcional.
- `handle`: `usuario@instancia` resoluble vía WebFinger.
- `schema_version`: versión del schema declarada por el nodo en su manifiesto (actual: `1`).

## Endpoints de federación

### Identidad y directorio

- `GET /api/federation/manifest` — manifiesto del nodo con `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` y `certificate_chain`. Firmado con la clave privada del certificado TLS del nodo.
- `GET /api/federation/directory` — lista de nodos confiados (`trusted_nodes`) con `allowed = true`, incluyendo `cert_fingerprint_sha256`, `capabilities`, `consent_required`, `minimize_data`.
- `GET/POST /api/federation/nodes` — políticas de nodo (allowlist/blocklist): `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search`. Solo admin.

### Identidad federada y tokens (Fase 3)

- `GET /api/federation/.well-known/jwks.json` — clave pública RSA del nodo en formato JWKS para validar tokens de federación de pares.
- `POST /api/federation/token` — emite un JWT de federación firmado (RS256). Requiere identidad de nodo verificada vía mTLS.
- `POST /api/federation/peers/verify` — valida la identidad de un nodo remoto (dominio + certificado + manifiesto firmado).
- `POST /api/federation/peers/{domain}/revoke` — revoca un nodo confiado (admin).

### Usuarios, reportes y descubrimento

- `GET /api/federation/users/{ref}` — resuelve usuario por `uuid`, `did` o `handle`. Requiere peer mTLS verificado.
- `GET /api/federation/.well-known/webfinger` — resuelve `acct:user@domain`. Requiere peer mTLS verificado.
- `POST/GET/PATCH /api/federation/reports` — reporte de moderación entre nodos.

### Health y utilidades

- `GET /api/federation/health`, `/ping`, `/status`, `/info`, `/version`, `/capabilities`, `/keys`, `/events`, `/peers`, `/links`, `/stats`, `/config`, `/heartbeat`, `/whoami`, `/aggregate-nodes`, `/ok`, `/yes`, `/no`, `/maybe`, `/always`, `/never` — endpoints de sondeo y diagnóstico.

## Ajustabilidad

- El schema es versionado; los nodos declaran `schema_version` en el manifest.
- Campos opcionales (`did`, `handle`) pueden omitirse si el nodo no los soporta.
- La minimización de datos (`minimize_data`) permite omitir campos sensibles en peering.
