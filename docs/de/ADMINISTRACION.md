# Administration — Clakettes

[ES](../es/ADMINISTRACION.md) · [EN](../en/ADMINISTRACION.md) · [FR](../fr/ADMINISTRACION.md) · [DE](ADMINISTRACION.md) · [IT](../it/ADMINISTRACION.md) · [CA](../ca/ADMINISTRACION.md) · [EU](../eu/ADMINISTRACION.md) · [GL](../gl/ADMINISTRACION.md) · [OC](../oc/ADMINISTRACION.md)

Anleitung für den Betrieb eines Deployments. Infrastruktur in [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), Produktions-Checkliste in [SEGURIDAD.md](SEGURIDAD.md).

## Startkonto

In Non-Prod (`APP_ENV != production`) erstellt der Start `admin` / `setup` (`admin@clakettes.com`, Admin-Rolle), falls es nicht existiert; in Prod **wird es nicht erstellt**. Ändere das Passwort bei der ersten Anmeldung. Die Anmeldung nutzt `POST /api/users/login` (JWT 30 min + refresh 30 d, Sitzungen auflisten und widerrufen unter `/api/auth/sessions`).

## `/api/admin`-Endpoints (nur Admin-Rolle, sonst 403)

| Methode und Route | Wirkung |
|---|---|
| `GET /api/admin/stats` | Zähler: Nutzer, Festivals, Kurzfilme, Nachrichten, aktive |
| `GET /api/admin/tables` | Tabellen (außer `alembic_version`) mit Zeilenanzahl |
| `GET /api/admin/audit-log` | Audit-Spur (Filter `action`, `actor_user_id`) |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400, wenn `confirm` nicht `yes` ist, 403, wenn das Passwort nicht verifiziert; eigenes Rate-Limit 3/300s (429, Umgehung mit `TESTING=true`) |

## Secrets und Rotation

- `SECRET_KEY`: in Prod zwingend (der Start schlägt mit dem Beispielschlüssel fehl und weist auf `secrets.token_urlsafe(64)` hin). Die Rotation invalidiert alle JWTs und Refresh-Tokens: in einem Wartungsfenster durchführen und ankündigen (alle müssen sich neu anmelden).
- `CORS_ORIGINS`: explizite Origins in Prod; `*` + Credentials ist verboten und blockiert den Start.
- Hinter Proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + Frontend-TLS.

## Föderation

| Operation | Endpoint / Tool | Wirkung |
|---|---|---|
| Knoten und Richtlinien | `GET/POST /api/federation/nodes` | Allowlist/Blocklist mit `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search` (Admin) |
| Peer-Identität | `GET /api/federation/whoami` | Validiert das RS256-JWT des Peers gegen sein JWKS; 401, wenn ungültig |
| Portabilität | `POST /api/federation/portability/bundles`, `/imports`, `/festivals/{id}/migrate`, `/users/{ref}/migrate`, `GET /redirects/{ref}` | Bundles signiert exportieren/importieren, Eigentum und Identität migrieren und alte Refs auflösen (Migrationen nur Admin) |
| Chat und Moderation | `/api/federation/chat/bridge/{inbound,outbound,config}`, `GET /api/federation/chat/messages`, `/api/chat/moderation/*` | Signierte Bridge, deduplizierter Verlauf, Meldungen, Mutes, Wortfilter und Limit von 10 Nachrichten/60 s pro Knoten und Nutzer |
| Ereignisse | `GET /api/federation/events/stream`, `POST /publish`, `GET /retry-queue` | SSE mit `since` und Herzschlag, Veröffentlichung an Peers und Wiederholungen (3 Versuche, 300 ms → 1,5 s → 5 s) |
| Resilienz | `GET /api/federation/resilience/{health,heartbeat,metrics,incident-plan}`, `POST /keys/revoke`, `GET /keys/revoked` | Health, Heartbeat, p50/p95-Metriken, sofortiger Schlüssel-Widerruf und Incident-Plan |
| Konformität | `python tools/federation_conformance.py <url> [--json]` | Prüft einen Drittknoten; Exit 1 bei kritischen/hohen Fehlern |

Das Detail des Vertrauensmodells und des Transports steht in [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) und [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md).

## Backups und Migrationen

- SQLite: `*.db` im gestoppten Zustand kopieren (zuerst `-Kill`). MariaDB: `mariadb-dump` (Volume `db-data`).
- Migrationen: `alembic upgrade head` aus `backend/` (Prod **nur** Alembic, nie `create_all`). Die jüngsten Migrationen fügen `identity_redirects`, `migration_audits`, `chat_outbox`, `message_reports`, `chat_mutes`, die Sitzplatz-Eindeutigkeit (`uq_event_seat_location`) und `contest_type` in Kurzfilmen mit obligatorischem `festival_id` hinzu.
- Engine-Wechsel: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); Details in [DATABASE.md](DATABASE.md).

## Fehlerbehebung

| Symptom | Wahrscheinliche Ursache | Maßnahme |
|---|---|---|
| Start bricht wegen `SECRET_KEY` / CORS ab | unsicherer Default oder `*` in Prod | Explizite `SECRET_KEY` und `CORS_ORIGINS` definieren |
| `401` bei öffentlichen Formular-Endpoints | falsch generierter Link | Link-Token prüfen; anonymer Zugriff allein verursacht keine 401 |
| `403` bei Festival-/Kanal-/Komitee-Verwaltung | Aufrufer ohne Rolle | Mitgliedschaft und Rolle prüfen (`GET …/members`); Auto-Join gibt nur `attendee` |
| `409` beim Beitritt | bereits Mitglied | `leave` verwenden oder über Mitglieder verwalten |
| `413` beim Upload | überschreitet 10 MB Body / 5 MB Bild / 100 MB Video / 10 MB PDF | Datei komprimieren oder teilen |
| `429` flächendeckend | Rate-Limit 100/60s pro IP (oder 3/300s bei Reset) | Warten und erneut versuchen; restliches `TESTING=true` prüfen |
| WS verbindet nicht | JWT ohne `type=access` oder widerrufene/abgelaufene Sitzung | Neu anmelden; `/api/auth/sessions` prüfen |
| Offline-App synchronisiert nicht | Queue mit erschöpften Fehlern (`failed`, 3 Versuche + Backoff) | Fehler in der Sync-Eingabe prüfen; `clear()` nach Bestätigung beim Logout |
| `403` beim Bundle-Import | `origin_domain` in der Knotenrichtlinie nicht erlaubt | `/api/federation/nodes` prüfen und erneut importieren |
| `429` im föderierten Chat | mehr als 10 Nachrichten/60 s pro Knoten und Nutzer | Auf `Retry-After` warten; in Tests mit `TESTING=true` deaktiviert |
| SSE-Ereignisse abgeschnitten oder ohne Daten | ungültiger Token oder `since` vor dem Replay | Neu anmelden und mit `since=0` neu starten (Replay von 200 Ereignissen) |
| Doppelte föderierte Nachrichten | erneuter Versand der Bridge | Nach `message_id` in `chat_outbox` verworfen; `/api/federation/chat/messages` prüfen |

## Siehe auch

- [USO.md](USO.md): Systemstart und Betrieb
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): Deployment, Ports und CI
- [SEGURIDAD.md](SEGURIDAD.md): Härtungs-Checkliste und Richtlinien
- [../README.md](../../README.md): globaler Projektkontext
