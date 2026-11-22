# Architettura — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](../fr/ARQUITECTURA.md) · [DE](../de/ARQUITECTURA.md) · [IT](ARQUITECTURA.md) · [CA](../ca/ARQUITECTURA.md) · [EU](../eu/ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](../oc/ARQUITECTURA.md)

## Mappa

```
Flutter (web/desktop/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                           rate limit 100/60s (?page=&size=)
```

Porte (Docker): backend `8000`, frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, dettaglio in [BACKEND.md](BACKEND.md) e [DATABASE.md](DATABASE.md))

Livelli: Routers → Services → Models, tipi tramite `app.enums`.

| Parte | Dove | Regola |
|---|---|---|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | I router non interrogano; i servizi non sollevano 404 (tranne 3 ereditati) |
| 404 uniforme | `routers/dependencies.py:get_or_404` | fetch → 404 in una riga |
| Auth | `app/auth.py:validate_access_token` | Firma + `type=access` + sessione attiva/non revocata/non scaduta; helper `hash_token()`, `is_expired()` (naive = UTC), `get_user_with_roles()` e `touch_session()` (`last_used_at` lazy, 5 min) |
| Auth opzionale | `routers/dependencies.py:get_current_user_optional` | Endpoint pubblici senza 401 |
| Permessi | `routers/permissions.py` | `require_admin(user, db)` unificato (ruolo legacy `admin` o `UserRole` `ACTIVE`/`APPROVED`), `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*`, `require_self_or_admin` (alias) e `require_owner_or_admin` (blocchi) |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, bucket `middleware:`/`dav:`; istanze in `main`/`admin`/`auth`/`auth_sessions`/`federation`) | 100/60 s globale, 600/60 s `/dav`, 5/300 s login, 20/60 s refresh, 3/300 s reset, federation 60/60 s; bypass centralizzato in `app.config.is_testing()` (`1/true/yes/on`) |
| Chat realtime | `app/chat_backend/` (WebSocket) + REST in `routers/chat.py` | Il WS valida la sessione tramite `validate_access_token` |
| Chat federato | `routers/federation_chat_bridge.py`, `services/message_queue_service.py` (`chat_outbox`), `chat_backend/durable_queue_backend.py` (`DurableQueueBackend`), `services/message_federation_service.py` | Bridge firmato RS256, dedup per `message_id`, ordinamento per `timestamp`, trasporto intercambiabile |
| Moderazione chat | `routers/chat_moderation.py`, `services/chat_moderation_service.py`, `services/chat_rate_limit_service.py` | Segnalazioni, mute, filtro parole, `disable_chat` e 10 messaggi/60 s per nodo e utente (off con `TESTING` ∈ {1,true,yes,on}) |
| Bus eventi | `routers/federation_events.py`, `services/event_bus_service.py` | SSE con `since`, battito e replay (200); pubblicazione firmata e 3 ripetizioni (300 ms → 1,5 s → 5 s) |
| CalDAV | `app/dav/` + `routers/dav.py` (prefisso `/dav`, bucket proprio 600/60s) | Token bearer nell'URL; TLS obbligatorio in prod |
| Export | `services/export_service.py` | CSV/ICS in stdlib; PDF con reportlab in import lazy |
| Migrazioni | `alembic/` (45 versioni, head `d1e2f3a4b5c6`) | Prod solo Alembic; dev anche `create_all` |
| Federazione | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py`, `services/node_peering_service.py`, `services/federation_token_service.py`, `app/mtls.py` | manifesto firmato RSA-SHA256, directory, nodi, segnalazioni, webfinger, users ref, JWKS, `whoami`, token federato, peers/verify, peers/revoke, mTLS per CN/PEM |
| Portabilità | `routers/federation_portability.py`, `services/portability_service.py`, modelli `identity_redirect`/`migration_audit` | Bundle firmati, import, migrazione festival/utenti e redirect |
| Resilienza | `routers/federation_resilience.py`, `services/federation_metrics_service.py` | Health, heartbeat, metriche p50/p95, revoca chiavi e piano incidente |
| Conformità | `tools/federation_conformance.py`, `services/federation_conformance_service.py` | CLI che verifica manifesto, JWKS, token, directory, portabilità, bridge e SSE |

API generata: `python tools/gen_api.py --all` produce 446 endpoint in 43 router (39 con prefisso in `main.py`; il generatore combina inoltre il prefisso di ogni `APIRouter` e rileva le dipendenze di auth, vedi [API.md](API.md)).

## Frontend (`frontend/`)

Servizi singleton + `setState()` + Streams (senza Provider). Avvio in `main()`:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `NodeService` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Parte | Dove | Regola |
|---|---|---|
| API | `services/api_service.dart` (nucleo) + `services/api/` (13 domini, split implementato, vedere il loro README) | Base `BACKEND_URL` (salvata > dart-define > default piattaforma; emulatore Android `10.0.2.2`); `resolveMediaUrl()` antepone il nodo attivo a `/uploads/...`; `uploadFile()` usa MIME per estensione, Bearer, ripetizione 401/refresh e fallback tra nodi; il WS della chat deriva il proprio URL dallo stesso `rootUrl` |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, 3 tentativi + backoff, anti-reinvio) | Cache con etichetta di nodo (`putWithOrigin`, `getOrigin`, `getEnvelope`, `listOrigins`, `clearOrigin`, `reconcile`); `ConnectivityMonitor` espone `NodeHealth`, `nodeHealth`, `offlineNodeCount`, `isDegraded` e sonde `ApiService.testNode()`; alla riconnessione, sync con conferma |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | WS in vivo, REST per cronologia e cronologia federata; E2EE ECDH P-256 + AES-GCM in isolate; `ChatPresenceBackend` fornisce indicatore di scrittura, latenza e conferme di lettura; ricerca locale, dedup e ordinamento per `(created_at,id)`; messaggi offline accodati in modo duraturo con lo stesso `message_id` |
| Avvisi | `notification_service.dart` | Desktop: plugin SO; web: Notification API; mobile: no-op (vedi [PUSH.md](PUSH.md)) |
| Navigazione | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer sempre; 11 schermate in cache; `DegradedNodesBanner` avvisa dei nodi che non rispondono con conteggio e ripetizione (`checkNow()`) |
| i18n | `l10n/` + `assets/l10n/` (9 locali, 823 chiavi per ARB) | `app_en.arb` è fallback; parità di chiavi e placeholder in `test/l10n/arb_parity_test.dart` (referenza `es`); `LocaleService.load()` rileva il locale del SO e persiste quello risolto |
| Permessi SO | `AndroidManifest.xml` / `Info.plist` | Rete, posizione, fotocamera, libreria foto, allarmi esatti |

## Flussi chiave

1. **Prenotazione**: festival → evento → posti in bulk (1 commit) → prenotazione → occupazione (pin in `tests/integration/test_flows.py`).
2. **Messaggio**: canale → membro → DM → lettura → cancellazione (solo mittente/admin).
3. **Delegazione**: creare → elencare attive → revocare (solo delegante/admin).
4. **Iscrizione pubblica**: link con token → modulo senza auth → approvazione.
5. **Portabilità**: bundle firmato → import con politica di origine → migrazione festival/utente → redirect della vecchia ref.
6. **Chat federato**: busta firmata → verifica firma e dedup → persistenza in `chat_outbox` → diffusione e ordinamento per `timestamp`.
7. **Eventi**: pubblicazione sul bus → SSE con `since` e battito → ripetizione con backoff se il peer fallisce.
8. **Corti nel festival**: creazione in `/api/festivals/{id}/shortfilms` con `contest_type` (`official_section` predefinito o `contest`) → `FestivalDetailResponse` con conteggio e riepilogo → filtro nell'app → proiezioni solo con corti dello stesso festival.
9. **Media**: caricamento multipart → percorso relativo `/uploads/...` (MIME da magic bytes, metadati ripuliti) → `resolveMediaUrl()` lo risolve contro il nodo attivo → cache Hive per nodo.
