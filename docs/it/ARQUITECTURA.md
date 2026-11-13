# Architettura — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](../fr/ARQUITECTURA.md) · [DE](../de/ARQUITECTURA.md) · [IT](ARQUITECTURA.md) · [CA](../ca/ARQUITECTURA.md) · [EU](../eu/ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](../oc/ARQUITECTURA.md)

## Mappa

```
Flutter (web/desktop/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                          rate limit 100/60s (?page=&size=)
```

Porte (Docker): backend `8000`, frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, dettagli in [BACKEND.md](BACKEND.md) e [DATABASE.md](DATABASE.md))

Layer: Routers → Services → Models, tipi via `app.enums`.

| Pezzo | Dove | Regola |
|-------|------|--------|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | I router non interrogano; i servizi non sollevano 404 (eccetto 3 ereditati) |
| 404 uniforme | `routers/dependencies.py:get_or_404` | fetch → 404 in una riga |
| Auth | `app/auth.py:validate_access_token` | Firma + `type=access` + sessione attiva/non revocata/non scaduta; `last_used_at` lazy (5 min) |
| Auth opzionale | `routers/dependencies.py:get_current_user_optional` | Endpoint pubblici senza 401 |
| Permessi | `routers/permissions.py` | `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*` |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, bucket `middleware:`/`dav:`; istanze in `main`/`admin`/`auth`) | Disattivato con `TESTING=true` |
| Chat in tempo reale | `app/chat_backend/` (WebSocket) + REST in `routers/chat.py` | WS valida sessione via `validate_access_token` |
| CalDAV | `app/dav/` + `routers/dav.py` (prefisso `/dav`, bucket proprio 600/60s) | Token bearer in URL; TLS obbligatorio in prod |
| Export | `services/export_service.py` | CSV/ICS in stdlib; PDF con reportlab in import pigro |
| Migrazioni | `alembic/` (36 versioni) | Prod solo Alembic; dev anche `create_all` |
| Federazione | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py` | manifest, directory, nodi, report, webfinger, rif user |

Conteggi reali (verificati su disco):

| Componente | File | Nota |
|------------|------|------|
| Router | 40 (38 con `APIRouter`) | `dependencies.py` e `permissions.py` sono helper senza router |
| Servizi | 43 | + `__init__.py` |
| Modelli entità | 40 | + `base.py` e `__init__.py` |
| Schemi | 37 | |
| Migrazioni Alembic | 36 | + `__init__.py` |
| File di test | 47 | `test_*.py` |
| Linee `def test_` | 1439 | |

## Frontend (`frontend/`)

Servizi singleton + `setState()` + Streams (nessun Provider). Avvio in `main()`:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Pezzo | Dove | Regola |
|-------|------|--------|
| API | `services/api_service.dart` (nucleo) + `services/api/` (9 domini) | Base `BACKEND_URL` (salvata > dart-define > default per piattaforma; emulatore Android `10.0.2.2`) |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, retry 3 + backoff, anti-rinvio) | Alla riconnessione, sync con conferma |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | WS live, REST per cronologia; E2EE ECDH P-256 + AES-GCM in isolate |
| Notifiche | `notification_service.dart` | Desktop: plugin SO; web: Notification API; mobile: no-op (vedi [PUSH.md](PUSH.md)) |
| Navigazione | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer sempre; 10 schermate memorizzate |
| i18n | `l10n/` + `assets/l10n/` (9 locali) | `en.arb` è fallback; 0 chiavi mancanti (verificato con script) |
| Permessi SO | `AndroidManifest.xml` / `Info.plist` | Rete, posizione, fotocamera, fototeca, allarmi esatti |

Conteggi reali (verificati su disco):

| Componente | File | Nota |
|------------|------|------|
| Widget riutilizzabili | 32 | in `lib/widgets/` |
| Schermate | 36 | in `lib/screens/` |
| File di test | 75 | `*_test.dart` in `test/` e sottocartelle |

## Flussi chiave

1. **Prenotazione**: festival → evento → posti bulk (1 commit) → prenotazione → occupazione (pin in `tests/integration/test_flows.py`).
2. **Messaggio**: canale → membro → DM → lettura → cancellazione (solo mittente/admin).
3. **Delegazione**: creare → elencare attive → revocare (solo delegante/admin).
4. **Registrazione pubblica**: link con token → form senza auth → approvazione.