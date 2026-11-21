# Protocol de federació Clakettes (fases 2 a 10)

Passos per crear un servidor/client interoperable:

1. Implementar els endpoints `/api/federation/*` (vegeu `docs/es/FEDERATION_SCHEMA.md`).
2. Configurar TLS obligatori entre nodes amb mTLS mutu (Fase 2): certificat emès per una CA de confiança, sense self-signed en producció.
3. Registrar el node com a confiat a cada pare amb el qual farà peering (`trusted_nodes`: domini, huella SHA-256 del PEM del certificat, CN del subject, capacitats, polítiques). `POST /api/federation/nodes` desa `import_only`, `disable_chat` i `disable_search` juntament amb `consent_required` i `minimize_data`.
4. Exposar el manifest a `GET /api/federation/manifest` amb `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` i `certificate_chain`. El manifest es signa en RSA-SHA256 (PKCS#1 v1.5) amb la clau privada del certificat TLS del node; el pare valida la signatura amb el PEM de `certificate_chain` i comprova `expires_at` (24 h).
5. Exposar la clau pública a `GET /api/federation/.well-known/jwks.json` perquè els pares validin els tokens de federació.
6. Validar tokens dels pares via JWKS: un node remot que crida un endpoint protegit ha de presentar un Bearer JWT signat (RS256) el `iss` del qual sigui el seu domini i la signatura del qual es validi contra el seu JWKS. `GET /api/federation/whoami` retorna la identitat del pare només quan aquest JWT valida (401 en cas contrari).
7. Resoldre usuaris remots via `GET /api/federation/users/{ref}` i `GET /api/federation/.well-known/webfinger` (ambdós requereixen peer mTLS verificat).
8. Fer servir Clakettes Schema v1 per a l'intercanvi de dades.
9. Portar identitat i dades amb `POST /api/federation/portability/bundles` i `/imports` (signatura HMAC-SHA256 i checksum), migrar amb `/festivals/{id}/migrate` i `/users/{ref}/migrate`, i resoldre refs antigues amb `GET /redirects/{ref}`.
10. Lliurar xat pel bridge signat `/api/federation/chat/bridge/{inbound,outbound,config}`; l'historial es consulta a `/api/federation/chat/messages`, amb deduplicació per `message_id` i ordre per `timestamp` + `message_id`. La cua durable `chat_outbox` permet transport intercambiable (detall a `docs/es/FEDERATION_CHAT_BROKER.md`).
11. Propagar canvis pel bus d'esdeveniments: `GET /api/federation/events/stream` (SSE amb `since` i batec), `POST /publish` i `GET /retry-queue` (3 intents, backoff 300 ms → 5 s).
12. Vigilar la salut del peering amb `/api/federation/resilience/{health,heartbeat,metrics,keys/revoke,keys/revoked,incident-plan}`; `metrics` exposa p50/p95, latència, fallades i reintents.
13. Verificar la conformitat d'un node tercer amb `python tools/federation_conformance.py <url> [--json]` (1 si hi ha fallades crítiques/altes).

## Motivació

El protocol permet que nodes independents intercanviïn festivals, usuaris i missatges sense perdre identitat ni traçabilitat.

## Ajustos

- `consent_required`: exigeix consentiment explícit abans de federar dades d'un node.
- `import_only`: federació unidireccional (només importar, no exportar).
- `disable_chat`/`disable_search`: permisos per funció per node.
- `minimize_data`: no compartir més del necessari en el peering.

## Endpoints clau

| Endpoint | Mètode | Descripció |
|---|---|---|
| `/api/federation/manifest` | GET | Manifest signat RSA-SHA256 amb `expires_at` i `certificate_chain` |
| `/api/federation/directory` | GET | Directori de nodes confiats |
| `/api/federation/nodes` | GET/POST | Polítiques d'allowlist/blocklist (`import_only`, `disable_chat`, `disable_search`) |
| `/api/federation/whoami` | GET | Identitat del pare, validant el seu JWT contra el seu JWKS |
| `/api/federation/.well-known/jwks.json` | GET | Clau pública JWKS del node |
| `/api/federation/token` | POST | Emissió de JWT de federació (RS256) |
| `/api/federation/peers/verify` | POST | Verificació d'identitat de node remot (CN i PEM del certificat) |
| `/api/federation/peers/{domain}/revoke` | POST | Revocació de node confiat (admin) |
| `/api/federation/users/{ref}` | GET | Resolució d'usuari remot (mTLS) |
| `/api/federation/.well-known/webfinger` | GET | WebFinger `acct:user@domain` (mTLS) |
| `/api/federation/reports` | POST/GET/PATCH | Reportes de moderació entre nodes |
| `/api/federation/portability/bundles`, `/imports` | POST | Exportació i importació de bundles signats |
| `/api/federation/portability/festivals/{id}/migrate`, `/users/{ref}/migrate` | POST | Migració de festivals i identitat d'usuari (admin) |
| `/api/federation/portability/redirects/{ref}` | GET | Resolució de la ref antiga després de la migració |
| `/api/federation/chat/bridge/inbound`, `/outbound`, `/config` | POST/GET | Bridge de xat signat i la seva configuració |
| `/api/federation/chat/messages` | GET | Historial federat, deduplicat i ordenat |
| `/api/chat/moderation/*` | POST/PATCH/GET | Reportes, silenciaments, filtre i límit de xat |
| `/api/federation/events/stream`, `/publish`, `/retry-queue` | GET/POST | SSE amb `since` i batec, publicació i reintents |
| `/api/federation/resilience/health`, `/heartbeat`, `/metrics` | GET | Salut, batec i mètriques reals p50/p95 |
| `/api/federation/resilience/keys/revoke`, `/keys/revoked`, `/incident-plan` | POST/GET | Revocació de claus i pla d'incidents |
