# Verwendung — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Schnellstart

| Ich möchte | Befehl |
|---|---|
| Alles lokal | `.\start.ps1` oder `./start.sh` (Docker, falls vorhanden, sonst lokal) |
| Nur Backend / Frontend | `-NoFrontend` / `-NoBackend` |
| Im Browser testen | `-Web` (lokaler Modus) |
| Lokale Produktion | `-Final` (Web-Build + Serve) |
| Tests | `-TestBackend` / `-TestFrontend` |
| Migrationen / mit MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Alles stoppen | `-Kill` |
| Fehlende Abhängigkeiten installieren | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: OS-Paketmanager + git clone) |
| Umgebung ohne Start prüfen | `-Check` (Doctor: Docker, Python, Flutter, .venv, Ports; Exit 1, wenn etwas fehlt) |
| Verteilbare Builds | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Ohne Docker erzeugt der Launcher eine lokale Bare-Metal-Umgebung: erkennt Python 3.12+ und Flutter, zeigt die Installation je nach OS und bietet die Installation per `-InstallMissing` an (fragt vorher, außer wenn das Flag gesetzt ist).

Dev-URLs: Backend `http://localhost:8000` (Swagger unter `/docs`), Frontend `http://localhost:3000`.
Wenn der Port belegt ist, wird automatisch ein neuer vergeben (siehe `[PUERTO]` in der Ausgabe).
Initial-Admin (nur Non-Prod): `admin` / `setup` — bei der ersten Anmeldung ändern.

## Konfiguration

| Variable / Flag | Wo | Wirkung |
|---|---|---|
| `BACKEND_URL` | `--dart-define` oder Backend-Bildschirm in der App | API-URL (in SharedPreferences persistiert) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; in Docker `./data/clakettes.db`) oder `mariadb+pymysql://…?ssl_ca=…` (prod, TLS zwingend) |
| `SECRET_KEY` | env (zwingend bei `APP_ENV=production`) | Signiert JWT; unsicherer Default blockiert den Start in Prod |
| `CORS_ORIGINS` | env | Explizite Origins in Prod (`*` mit Credentials verboten) |
| `APP_ENV` | env | `development` erstellt Admin + `create_all`; `production` erfordert Alembic |
| `PUBLIC_BASE_URL` | `backend/.env` | Öffentliche Domain des Knotens; erscheint im Manifest und in Portabilitäts-Bundles |
| `MTLS_REQUIRED` | env | Erzwingt verifiziertes Peer-mTLS in der Föderation (CN und PEM des Zertifikats) |
| `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | env | PEM des Zertifikats und privater Schlüssel, die das Manifest signieren (RSA-SHA256) |

## Betrieb

- **Migrieren**: `alembic upgrade head` aus `backend/` (Docker: `-Migrate`).
- **Automatische Migration**: die App migriert die DB beim Start selbst und versiegelt neue DBs mit der aktuellen Revision; `SKIP_AUTO_MIGRATE=1` zum Überspringen (extern verwaltete DBs).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; zurück mit `import_mariadb_to_sqlite.py` (Details in [DATABASE.md](DATABASE.md)).
- **Backups**: SQLite = `*.db` kopieren; MariaDB = `mariadb-dump` (Volume `db-data` in Docker).
- **Logs**: uvicorn-stdout (DAV-Tokens redigiert); API-Fehler in SnackBar + `debugPrint`.
- **Limits**: Bodies ≤10 MB (413 bei größer); Rate-Limit mit 429 + Wiederholung (federation 60/60 s pro IP; Chat 10/60 s pro Knoten und Nutzer, deaktiviert mit `TESTING=true`).
- **Föderation**: einen Drittknoten prüfen mit `python tools/federation_conformance.py <url> [--json]`; die Peering-Gesundheit liegt unter `/api/federation/resilience/health` und die p50/p95-Metriken unter `/metrics`.
- **Portabilität**: Bundles exportieren/importieren über `/api/federation/portability/{bundles,imports}` und Identitäts-Redirects unter `/redirects/{ref}` abfragen.

## Nutzerrollen

`admin` (alles) → `organizer` (sein Festival: Events, Formulare, Komitees) → `attendee`/`juror`/usw. (von Organizers zugewiesen; Auto-Join gibt nur `attendee`). Kanäle: `admin`/`moderator`/`member`; Komitees mit Mitgliederanzahl in der Liste.

## Funktionen in aktiver Entwicklung

🚧 Die folgenden Funktionen sind in aktiver Entwicklung und können sich ändern:

- **Soziale Profile**: Veröffentlichungswände (Microblogging mit Markdown und Video-/Podcast-Einbettungen) auf Nutzer- und Festival-Profilen, mit optionalen Antwort-Threads pro Veröffentlichung und Moderation nach Rollen (Administratoren, Festival-Leitung, Moderatoren). Derzeit keine Reaktionen, Sticker oder GIFs.
- **Profil-Anpassung**: Titelbild, Tagline und soziale Links bei Nutzern und Festivals.
- **Abzeichen**: standardmäßig deaktiviert; nur das Admin-Team kann sie aktivieren (`PUT /api/badges/settings`). Plattform-Abzeichen werden von Administratoren vergeben; Festival-Verdienstabzeichen (Veteran, beliebt, Rolle, Sonderpreis), deren Verwaltung. Jedes Abzeichen hat ein Bild (SVG bevorzugt).
- **Jury-Abstimmung**: Bewertung pro Werk, Aggregation und optionale Anonymität (Phase 5 der Roadmap).

## Siehe auch

- [README.md](../../README.md): allgemeine Projektbeschreibung und Schnellzugriff
- [HERRAMIENTAS.md](HERRAMIENTAS.md): Skripte und Ausführungsbefehle
- [ADMINISTRACION.md](ADMINISTRACION.md): Deployment-Administration und Secret-Rotation
- [SEGURIDAD.md](SEGURIDAD.md): Checkliste und Produktions-Best-Practices
