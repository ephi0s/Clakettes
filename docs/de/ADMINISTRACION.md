# Administration — Clakettes

[ES](../es/ADMINISTRACION.md) · [EN](../en/ADMINISTRACION.md) · [FR](../fr/ADMINISTRACION.md) · [DE](ADMINISTRACION.md) · [IT](../it/ADMINISTRACION.md) · [CA](../ca/ADMINISTRACION.md) · [EU](../eu/ADMINISTRACION.md) · [GL](../gl/ADMINISTRACION.md) · [OC](../oc/ADMINISTRACION.md)

Anleitung für den Betreiber einer Bereitstellung. Infrastruktur in [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), Produktions-Checkliste in [SEGURIDAD.md](SEGURIDAD.md).

## Erstes Konto

In Nicht-Produktion (`APP_ENV != production`) erstellt der Start `admin` / `setup` (`admin@clakettes.com`, Admin-Rolle), falls nicht vorhanden; in Produktion **wird es nicht erstellt**. Passwort beim ersten Login ändern. Login nutzt `POST /api/users/login` (JWT 30 Min + Refresh 30 Tage, Liste und Widerruf von Sitzungen unter `/api/auth/sessions`).

## `/api/admin`-Endpunkte (nur Admin-Rolle, sonst 403)

| Methode und Route | Wirkung |
|-------------------|---------|
| `GET /api/admin/stats` | Zähler: Nutzer, Festivals, Kurzfilme, Nachrichten, aktive |
| `GET /api/admin/tables` | Tabellen (außer `alembic_version`) mit Zeilenanzahl |
| `GET /api/admin/audit-log` | Audit-Spur (Filter `action`, `actor_user_id`) |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 wenn `confirm` nicht `yes`, 403 wenn Passwort nicht verifiziert; eigenes Rate-Limit 3/300s (429, Umgehung mit `TESTING=true`) |

## Geheimnisse und Rotation

- `SECRET_KEY`: obligatorisch in Produktion (Start schlägt mit Beispiel-Schlüssel fehl und gibt `secrets.token_urlsafe(64)` aus). Rotation ungültig alle JWT und Refresh-Tokens: in Wartungsfenster durchführen und warnen (alle loggen sich neu ein).
- `CORS_ORIGINS`: explizite Ursprünge in Produktion; `*` + Credentials ist verboten und blockiert den Start.
- Hinter Proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS-Vorfranz.

## Backups und Migrationen

- SQLite: `*.db` im angehaltenen Zustand kopieren (`-Kill` davor). MariaDB: `mariadb-dump` (Volume `db-data`).
- Migrationen: `alembic upgrade head` von `backend/` (36 Versionen; in Produktion **nur** Alembic, niemals `create_all`).
- Motorenwechsel: `python export_sqlite_to_mariadb.py` (Dev→Prod), `python import_mariadb_to_sqlite.py` (Prod→Dev); Details in [DATABASE.md](DATABASE.md).

## Fehlerbehebung

| Symptom | Wahrscheinliche Ursache | Aktion |
|---------|------------------------|--------|
| Start bricht ab wegen `SECRET_KEY` / CORS | unsicherer Standard oder `*` in Produktion | Explizite `SECRET_KEY` und `CORS_ORIGINS` definieren |
| `401` auf öffentlichen Formular-Endpunkten | falsch generierter Link | Link-Token prüfen; anonymer Zugriff verursacht nicht von allein 401 |
| `403` bei Verwaltung von Festival/Kanal/Komitee | Aufrufer ohne Rolle | Mitgliedschaft und Rolle prüfen (`GET …/members`); Auto-Join gibt nur `attendee` |
| `409` beim Beitreten | bereits Mitglied | `leave` verwenden oder über Mitglieder verwalten |
| `413` beim Hochladen | überschreitet 10 MB Körper / 5 MB Bild / 100 MB Video / 10 MB PDF | Datei komprimieren oder teilen |
| `429` allgemein | Rate-Limit 100/60s pro IP (oder 3/300s auf Reset) | Warten und wiederholen; Restliches `TESTING=true` prüfen |
| WS verbindet nicht | JWT ohne `type=access` oder widerrufene/abgelaufene Sitzung | Neu einloggen; `/api/auth/sessions` prüfen |
| App offline synchronisiert nicht | Warteschlange mit erschöpften Fehlern (`failed`, 3 Versuche + Backoff) | Fehler im Sync-Prompt prüfen; `clear()` nach Bestätigung beim Logout |

## Siehe auch

- [USO.md](USO.md): Systemstart und Betrieb
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): Bereitstellung, Ports und CI
- [SEGURIDAD.md](SEGURIDAD.md): Checkliste zur Verstärkung und Richtlinien
- [../README.md](../../README.de.md): globaler Projektkontext