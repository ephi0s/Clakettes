# Architektur — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](../fr/ARQUITECTURA.md) · [DE](ARQUITECTURA.md) · [IT](../it/ARQUITECTURA.md) · [CA](../ca/ARQUITECTURA.md) · [EU](../eu/ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](../oc/ARQUITECTURA.md)

## Karte

```
Flutter (Web/Desktop/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                          rate limit 100/60s (?page=&size=)
```

Ports (Docker): Backend `8000`, Frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, Details in [BACKEND.md](BACKEND.md) und [DATABASE.md](DATABASE.md))

Ebenen: Routers → Services → Models, Typen via `app.enums`.

| Stück | Wo | Regel |
|---|---|---|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Routers fragen nicht ab; Services werfen kein 404 (außer 3 geerbte) |
| Einheitlicher 404 | `routers/dependencies.py:get_or_404` | fetch → 404 in einer Zeile |
| Auth | `app/auth.py:validate_access_token` | Signatur + `type=access` + aktive/nicht widerrufene/nicht abgelaufene Session; `last_used_at` lazy (5 min) |
| Optionale Auth | `routers/dependencies.py:get_current_user_optional` | Öffentliche Endpunkte ohne 401 |
| Berechtigungen | `routers/permissions.py` | `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*` |
| Rate-Limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, Eimer `middleware:`/`dav:`; Instanzen in `main`/`admin`/`auth`) | Deaktiviert mit `TESTING=true` |
| Echtzeit-Chat | `app/chat_backend/` (WebSocket) + REST in `routers/chat.py` | WS validiert Session via `validate_access_token` |
| CalDAV | `app/dav/` + `routers/dav.py` (Präfix `/dav`, eigener Eimer 600/60s) | Bearer-Token in URL; TLS obligatorisch in Prod |
| Export | `services/export_service.py` | CSV/ICS in stdlib; PDF mit reportlab in Lazy Import |
| Migrationen | `alembic/` (36 Versionen) | Prod nur Alembic; Dev außerdem `create_all` |
| Föderation | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py` | Manifest, Verzeichnis, Knoten, Berichte, WebFinger, User-Ref |

Reale Zahlen (auf der Festplatte verifiziert):

| Komponente | Dateien | Hinweis |
|---|---|---|
| Router | 40 (38 mit `APIRouter`) | `dependencies.py` und `permissions.py` sind Helfer ohne Router |
| Dienste | 43 | + `__init__.py` |
| Entitätsmodelle | 40 | + `base.py` und `__init__.py` |
| Schemas | 37 | |
| Alembic-Migrationen | 36 | + `__init__.py` |
| Testdateien | 47 | `test_*.py` |
| Zeilen `def test_` | 1439 | |

## Frontend (`frontend/`)

Singleton-Dienste + `setState()` + Streams (kein Provider). Start in `main()`:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Stück | Wo | Regel |
|---|---|---|
| API | `services/api_service.dart` (Kern) + `services/api/` (9 Domänen) | Basis `BACKEND_URL` (gespeichert > dart-define > Plattform-Standard; Android-Emulator `10.0.2.2`) |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, Wiederholung 3 + Backoff, Anti-Resend) | Bei Wiederverbindung Sync mit Bestätigung |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | Live WS, REST für Verlauf; E2EE ECDH P-256 + AES-GCM in Isolates |
| Benachrichtigungen | `notification_service.dart` | Desktop: OS-Plugin; Web: Notification API; Mobil: no-op (siehe [PUSH.md](PUSH.md)) |
| Navigation | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer immer; 10 zwischengespeicherte Bildschirme |
| i18n | `l10n/` + `assets/l10n/` (9 locales) | `en.arb` ist Fallback; 0 fehlende Schlüssel (verifiziert mit Skript) |
| OS-Berechtigungen | `AndroidManifest.xml` / `Info.plist` | Netzwerk, Standort, Kamera, Fotobibliothek, genaue Alarme |

Reale Zahlen (auf der Festplatte verifiziert):

| Komponente | Dateien | Hinweis |
|---|---|---|
| Wiederverwendbare Widgets | 32 | in `lib/widgets/` |
| Bildschirme | 36 | in `lib/screens/` |
| Testdateien | 75 | `*_test.dart` in `test/` und Unterordnern |

## Zentrale Flows

1. **Reservierung**: Festival → Event → Bulk-Sitze (1 Commit) → Reservierung → Auslastung (gepinnt in `tests/integration/test_flows.py`).
2. **Nachricht**: Kanal → Mitglied → DM → Lesen → Löschen (nur Absender/Admin).
3. **Delegation**: Erstellen → Aktive auflisten → Widerrufen (nur Delegator/Admin).
4. **Öffentliche Registrierung**: Token-Link → Formular ohne Auth → Genehmigung.