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

Schichten: Routers → Services → Models, Typen über `app.enums`.

| Baustein | Wo | Regel |
|---|---|---|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Router fragen nicht ab; Services werfen keine 404 (außer 3 geerbten) |
| Einheitliche 404 | `routers/dependencies.py:get_or_404` | fetch → 404 in einer Zeile |
| Auth | `app/auth.py:validate_access_token` | Signatur + `type=access` + aktive/nicht widerrufene/nicht abgelaufene Sitzung; `last_used_at` lazy (5 min) |
| Optionale Auth | `routers/dependencies.py:get_current_user_optional` | Öffentliche Endpoints ohne 401 |
| Berechtigungen | `routers/permissions.py` | `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*` |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, Buckets `middleware:`/`dav:`; Instanzen in `main`/`admin`/`auth`) | Deaktiviert mit `TESTING=true` |
| Echtzeit-Chat | `app/chat_backend/` (WebSocket) + REST in `routers/chat.py` | WS validiert Sitzung über `validate_access_token` |
| Föderierter Chat | `routers/federation_chat_bridge.py`, `services/message_queue_service.py` (`chat_outbox`), `chat_backend/durable_queue_backend.py` (`DurableQueueBackend`), `services/message_federation_service.py` | RS256-signierte Bridge, Deduplizierung nach `message_id`, Sortierung nach `timestamp`, austauschbarer Transport |
| Chat-Moderation | `routers/chat_moderation.py`, `services/chat_moderation_service.py`, `services/chat_rate_limit_service.py` | Meldungen, Mutes, Wortfilter, `disable_chat` und 10 Nachrichten/60 s pro Knoten und Nutzer (aus mit `TESTING=true`) |
| Ereignis-Bus | `routers/federation_events.py`, `services/event_bus_service.py` | SSE mit `since`, Herzschlag und Replay (200); signiertes Publishing und 3 Wiederholungen (300 ms→5 s) |
| CalDAV | `app/dav/` + `routers/dav.py` (Präfix `/dav`, eigener Bucket 600/60s) | Bearer-Token in URL; TLS in Prod zwingend |
| Export | `services/export_service.py` | CSV/ICS in stdlib; PDF mit reportlab im Lazy-Import |
| Migrationen | `alembic/` (42 Versionen, Head `c1d2e3f4a5b6`) | Prod nur Alembic; dev zusätzlich `create_all` |
| Föderation | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py`, `services/node_peering_service.py`, `services/federation_token_service.py`, `app/mtls.py` | RSA-SHA256-signiertes Manifest, Verzeichnis, Knoten, Meldungen, Webfinger, users ref, JWKS, `whoami`, Föderations-Token, peers/verify, peers/revoke, mTLS nach CN/PEM |
| Portabilität | `routers/federation_portability.py`, `services/portability_service.py`, Modelle `identity_redirect`/`migration_audit` | Signierte Bundles, Imports, Festival-/Nutzer-Migration und Redirects |
| Resilienz | `routers/federation_resilience.py`, `services/federation_metrics_service.py` | Health, Heartbeat, p50/p95-Metriken, Schlüssel-Widerruf und Incident-Plan |
| Konformität | `tools/federation_conformance.py`, `services/federation_conformance_service.py` | CLI, die Manifest, JWKS, Token, Verzeichnis, Portabilität, Bridge und SSE prüft |

Generierte API: `python tools/gen_api.py --all` erzeugt 441 Endpoints in 39 Routern mit Präfix (siehe [API.md](API.md)).

## Frontend (`frontend/`)

Singleton-Services + `setState()` + Streams (kein Provider). Start in `main()`:
`DatabaseService` → `OfflineCache` → `SyncQueue` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Baustein | Wo | Regel |
|---|---|---|
| API | `services/api_service.dart` (Kern) + `services/api/` (9 Domänen) | Basis `BACKEND_URL` (gespeichert > dart-define > Plattform-Default; Android-Emulator `10.0.2.2`) |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, 3 Wiederholungen + Backoff, Anti-Resend) | Cache mit Knoten-Tag (`putWithOrigin`, `getOrigin`, `getEnvelope`, `listOrigins`, `clearOrigin`, `reconcile`); Health-Checks pro Knoten für elegante Degradation; bei Wiederverbindung Sync mit Bestätigung |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | Live-WS, REST für Verlauf und föderierten Verlauf; E2EE ECDH P-256 + AES-GCM in Isolates |
| Benachrichtigungen | `notification_service.dart` | Desktop: OS-Plugin; Web: Notification API; Mobil: no-op (siehe [PUSH.md](PUSH.md)) |
| Navigation | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer immer; 10 gecachte Bildschirme |
| i18n | `l10n/` + `assets/l10n/` (9 Locales) | `en.arb` ist Fallback; 0 fehlende Keys (per Skript geprüft) |
| OS-Berechtigungen | `AndroidManifest.xml` / `Info.plist` | Netzwerk, Standort, Kamera, Fotobibliothek, exakte Alarme |

## Schlüsselabläufe

1. **Reservierung**: Festival → Event → Sitzplätze in Bulk (1 Commit) → Reservierung → Belegung (Pin in `tests/integration/test_flows.py`).
2. **Nachricht**: Kanal → Mitglied → DM → lesen → löschen (nur Absender/Admin).
3. **Delegation**: erstellen → aktive auflisten → widerrufen (nur Delegierender/Admin).
4. **Öffentliche Anmeldung**: Link mit Token → Formular ohne Auth → Freigabe.
5. **Portabilität**: signiertes Bundle → Import mit Ursprungsrichtlinie → Festival-/Nutzer-Migration → Redirect der alten Ref.
6. **Föderierter Chat**: signiertes Envelope → Signaturprüfung und Deduplizierung → Persistenz in `chat_outbox` → Verteilung und Sortierung nach `timestamp`.
7. **Ereignisse**: Veröffentlichung im Bus → SSE mit `since` und Herzschlag → Wiederholung mit Backoff bei Peer-Fehler.
