# Nutzung — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Schneller Start

| Ich möchte | Befehl |
|---|---|
| Alles lokal | `.\start.ps1` oder `./start.sh` (Docker wenn verfügbar, lokal wenn nicht) |
| Nur Backend / Frontend | `-NoFrontend` / `-NoBackend` |
| Im Browser testen | `-Web` (lokaler Modus) |
| Lokale Produktion | `-Final` (Web-Build + Serve) |
| Tests | `-TestBackend` / `-TestFrontend` |
| Migrationen / mit MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Alles stoppen | `-Kill` |
| Fehlende Abhängigkeiten installieren | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: OS-Paketmanager + git clone) |
| Umgebung prüfen ohne Start | `-Check` (Doctor: Docker, Python, Flutter, .venv, Ports; endet mit 1 wenn etwas fehlt) |
| Verteilbare Builds | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Ohne Docker erstellt der Launcher eine bare-metal lokale Umgebung: erkennt Python 3.12+ und Flutter, zeigt die Installation gemäß Ihrem Betriebssystem an und bietet Installation mit `-InstallMissing` (fragt vorher, außer Sie übergeben das Flag).

Dev-URLs: Backend `http://localhost:8000` (Swagger unter `/docs`), Frontend `http://localhost:3000`.
Wenn der Port besetzt ist, wird er automatisch neu zugewiesen (siehe `[PUERTO]` in der Ausgabe).
Erstadmin (nur Nicht-Produktion): `admin` / `setup` — beim ersten Login ändern.

## Konfiguration

| Variable / Flag | Wo | Wirkung |
|---|---|---|
| `BACKEND_URL` | `--dart-define` oder Backend-Bildschirm in der App | API-URL (persistiert in SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; in Docker `./data/clakettes.db`) oder `mariadb+pymysql://…?ssl_ca=…` (Prod, TLS obligatorisch) |
| `SECRET_KEY` | env (obligatorisch in `APP_ENV=production`) | Signiert JWT; unsicherer Standard blockiert den Start in Prod |
| `CORS_ORIGINS` | env | Explizite Ursprünge in Prod (`*` mit Credentials verboten) |
| `APP_ENV` | env | `development` erstellt Admin + `create_all`; `production` erfordert Alembic |

## Betrieb

- **Migrieren**: `alembic upgrade head` von `backend/` (Docker: `-Migrate`).
- **Automatische Migration**: Die App migriert die DB selbst beim Start und versiegelt neue DBs mit der aktuellen Revision; `SKIP_AUTO_MIGRATE=1` zum Übersetzen (extern verwaltete DBs).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; zurück mit `import_mariadb_to_sqlite.py` (Detail in [DATABASE.md](DATABASE.md)).
- **Backups**: SQLite = `*.db` kopieren; MariaDB = `mariadb-dump` (Volume `db-data` in Docker).
- **Logs**: uvicorn stdout (DAV-Tokens redacted); API-Fehler in SnackBar + `debugPrint`.
- **Limits**: Körper ≤10 MB (413 wenn größer); Rate-Limit mit 429 + Wiederholung.

## Benutzerrollen

`admin` (alles) → `organizer` (sein Festival: Events, Formulare, Komitees) → `attendee`/`juror`/etc. (von Organizer zugewiesen; Auto-Join gibt nur `attendee`). Kanäle: `admin`/`moderator`/`member`; Komitees mit Mitgliederzahl in der Liste.

## Funktionen in aktiver Entwicklung

🚧 Die folgenden Funktionen befinden sich in aktiver Entwicklung und können sich ändern:

- **Social Profiles**: Veröffentlichungswände (Microblogging mit Markdown und Video/Podcast-Einbettungen) auf Benutzer- und Festivalprofilen, mit optionalen Antwort-Threads pro Veröffentlichung und Moderation durch Rollen (Administratoren, Festivalverwaltung, Moderatoren). Keine Reaktionen, Sticker oder GIFs fürs Erste.
- **Profilpersonalisierung**: Cover, Tagline und Social Links auf Benutzern und Festivals.
- **Badges**: standardmäßig deaktiviert; nur das Admin-Team kann sie aktivieren (`PUT /api/badges/settings`). Plattform-Badges werden von Administratoren vergeben; Festival-Verdienst-Badges (Veteran, Beliebt, Rolle, Sonderpreis), ihre Verwaltung. Jedes Badge trägt ein Bild (SVG bevorzugt).
- **Juryabstimmung**: Bewertung pro Werk, Aggregation und optionale Anonymität (Phase 5 der Roadmap).

## Siehe auch

- [README.md](../../README.de.md): allgemeine Projektbeschreibung und schneller Zugriff
- [HERRAMIENTAS.md](HERRAMIENTAS.md): Skripte und Ausführungsbefehle
- [ADMINISTRACION.md](ADMINISTRACION.md): Bereitstellungsverwaltung und Schlüsselrotation
- [SEGURIDAD.md](SEGURIDAD.md): Checkliste und Produktions-Best Practices