# Clakettes

Die Plattform, auf der Filmfestivals das ganze Jahr leben: Ausschreibungen, Kurzfilme, Teams, Spielstätten und Publikum an einem Ort.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Läuft auf Web, Android, iOS und Desktop (Windows, macOS, Linux), in 9 Sprachen und auch offline.

---

## Für wen ist es?

- **Festivals**: publiziere dein Festival, öffne Ausschreibungen, empfange Kurzfilme, organisiere Komitees und Jurys, verwalte Spielstätten und kommuniziere dein Palmarès.
- **Filmprofis**: erstelle dein Profil (Regie, Schauspiel, Ton, Drehbuch, Schnitt, Kostüm und mehr), zeige dein Palmarès und vernetze dich mit Festivals und Teams.
- **Express-Teams**: koordiniere deine Drehgruppe, geolokalisiere Teilnehmende und reiche deinen Kurzfilm bei Express-Wettbewerben ein.
- **Publikum**: entdecke Festivals, folge Kurzfilmen und kontaktiere die Community.

## Was du tun kannst

- **Festivals und Ausschreibungen**: jedes Festival kann mehrere offene Ausschreibungen mit eigenen Regeln und Anmeldeformularen haben.
- **Kurzfilme**: lade Kurzfilme hoch, verknüpfe sie mit Ausschreibungen und Drehorten.
- **Profile mit Palmarès**: Palmarès verknüpft mit Plattform-Festivals oder extern via Links, mit feldweiser Privatsphärenkontrolle.
- **Chat**: Direkt- und Gruppen-/Kanal-Nachrichten pro Festival, mit Ende-zu-Ende-Verschlüsselung.
- **Karten**: Spielstätten und Drehorte auf interaktiven Karten, mit Öffnen in deiner Lieblings-Kartenapp.
- **Offline**: die App läuft weiter offline und synchronisiert deine Änderungen bei Wiederverbindung.
- **In deiner Sprache**: Spanisch, Englisch, Französisch, Deutsch, Italienisch, Katalanisch, Baskisch, Galicisch und Okzitanisch, mit automatischer Erkennung.

## Anforderungen und Start

### Mindestanforderungen

- Python 3.12+
- Flutter SDK >= 3.0.0 y < 4.0.0
- Git
- Docker y Docker Compose para despliegue/entorno productivo
- Navegador con soporte para web (recomendado Chrome/Brave)

### Schnellstart

En Windows:

```bat
start.bat --dev
```

En PowerShell:

```powershell
./start.ps1 --dev
```

En Linux/macOS:

```bash
./start.sh --dev
```

Dies startet das Backend auf `http://localhost:8000` und die App im lokalen Modus; die API exponiert Swagger/OpenAPI unter `/docs`. Du kannst jede Seite mit `--no-backend` oder `--no-frontend` deaktivieren.

### Weitere nützliche Optionen

```bash
start.bat --help
start.bat --migrate
start.bat --build
start.bat --build-all
```

Die vollständige Start- und Deployment-Referenz in [docs/de/HERRAMIENTAS.md](docs/de/HERRAMIENTAS.md) und [docs/de/USO.md](docs/de/USO.md).

## Umgebungsvariablen und Konfiguration

### Backend

Erstelle oder passe `backend/.env` mit mindestens an:

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
```

Für die Produktionsumgebung wird MariaDB genutzt; Skripte und Deployment-Doku verwalten es mit Docker.

### Frontend

Die App nutzt das Backend per URL wieder, normal mit `--dart-define`:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

Der automatische Projektstart konfiguriert dies bereits, wenn `start.*` genutzt wird.

## Projektstatus

🚧 **In aktiver Entwicklung** — Festivals, Kurzfilme, Chat mit E2EE, Karten, Offline-Modus und 9 Sprachen lauffähig; mit Backend-Tests (~1400) und Frontend (75 Testdateien).

**Nächste Roadmap:**

- [ ] Push-Benachrichtigungen (Firebase/APNs)
- [ ] Signiertes Linux AppImage
- [ ] Windows MSI-Installer
- [x] Exportierbare OpenAPI-Dokumentation (`/openapi.json` ohne duplizierte operationIds + `docs/de/API.md` regeneriert)

## Projektdokumentation

Die Dok-Landkarte liegt in [docs/de/README.md](docs/de/README.md). Sie ist der beste Einstieg für jeden Nutzertyp:

- [docs/de/USO.md](docs/de/USO.md): Start, Betrieb, Umgebung und tägliche Nutzung
- [docs/de/ADMINISTRACION.md](docs/de/ADMINISTRACION.md): Administration, Konten und Bereitstellung
- [docs/de/INFRAESTRUCTURA.md](docs/de/INFRAESTRUCTURA.md): Docker, Ports, CI und Infrastruktur
- [docs/de/SEGURIDAD.md](docs/de/SEGURIDAD.md): Token, Richtlinien und Produktionscheckliste
- [docs/de/ARQUITECTURA.md](docs/de/ARQUITECTURA.md): Backend/Frontend-Architektur und zentrale Flows
- [docs/de/API.md](docs/de/API.md): Endpunkt-Referenz
- [docs/de/DESARROLLO.md](docs/de/DESARROLLO.md): wie man Endpoints oder Bildschirme hinzufügt
- [docs/de/BACKEND.md](docs/de/BACKEND.md): Backend-Anleitung (Ebenen, Konfiguration, Auth, Tests)
- [docs/de/DATABASE.md](docs/de/DATABASE.md): Schema und Migrationen
- [docs/de/FEDERATION_PROTOCOL.md](docs/de/FEDERATION_PROTOCOL.md): Föderationsprotokoll (Phase 4)
- [docs/de/FEDERATION_SCHEMA.md](docs/de/FEDERATION_SCHEMA.md): Clakettes Schema v1
- [docs/de/FEDERATION_SECURITY.md](docs/de/FEDERATION_SECURITY.md): federiertes Vertrauensmodell
- [docs/de/PUSH.md](docs/de/PUSH.md): Push-Benachrichtigungsentscheidung

Außerdem ist der Startpunkt für Entwicklung und Projektkonvention [AGENTS.md](AGENTS.md).

### Siehe auch

- [docs/de/README.md](docs/de/README.md): allgemeiner Index nach Zielgruppe
- [docs/de/HERRAMIENTAS.md](docs/de/HERRAMIENTAS.md): Build-, Test- und Startbefehle
- [docs/de/FUNCIONAL.md](docs/de/FUNCIONAL.md): realer Produktnutzen pro Rolle

### Kurzes FAQ

- **Brauche ich Docker für den Start?** Nein. Der lokale Start mit `start.*` läuft ohne Docker; Docker dient für Produktionsumgebung und reproduzierbare Builds.
- **Was tun, wenn die API nicht antwortet?** Prüfe, ob das Backend auf `http://localhost:8000` läuft und ob `/docs` antwortet.
- **Welches Dokument soll ich zuerst lesen?** Als Nutzer [docs/de/USO.md](docs/de/USO.md); als Entwickler [docs/de/ARQUITECTURA.md](docs/de/ARQUITECTURA.md).
- **Woran erkenne ich, ob eine Änderung Doku-Update braucht?** Wenn sie Start, API, Rollen, Berechtigungen, Env-Variablen oder Schema ändert, aktualisiere auch die entsprechende Dokumentation.

## Für Entwickler

> Vollständige Details in [`AGENTS.md`](AGENTS.md) (Architektur, Befehle und Konventionen) und im Index von [`docs/`](docs/de/README.md) (Anleitungen pro Rolle: funktional, Nutzung, Administration, Infrastruktur, Sicherheit, Architektur, API).

**Auf einen Blick**: FastAPI-Backend in Schichten (Router → Dienste → SQLAlchemy-Modelle, SQLite in Dev / MariaDB in Prod, JWT + Refresh, 36 Alembic-Migrationen); Flutter-Frontend Material 3 mit Dark Mode (Singletons + `setState()` + Streams, Hive offline, 32 wiederverwendbare Widgets).

```bash
# Tests
cd backend && python -m pytest tests/ -x -q --tb=short
cd frontend && flutter test

# Lint
cd backend && ruff check . && ruff format --check .
cd frontend && flutter analyze

# Migraciones
cd backend && alembic upgrade head
```

## Lokale Entwicklung

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
flutter run
```

## Deployment

```bash
docker compose --profile prod up -d
```

Backend + Frontend (nginx) + MariaDB. Die verteilten Builds (Web, Windows, Linux, Android) werden mit `start.bat --build-all` und der Skriptsammlung von [docs/de/HERRAMIENTAS.md](docs/de/HERRAMIENTAS.md) verwaltet.

## Fehlerbehebung

### Das Backend startet nicht

- Verifiziere, ob Python 3.12+ installiert ist.
- Prüfe, ob `backend/.env` existiert und gültig ist.
- Führe `cd backend && python -m uvicorn app.main:app --reload` aus, um den tatsächlichen Fehler zu sehen.

### Die App verbindet nicht mit der API

- Stelle sicher, dass das Backend unter `http://localhost:8000` läuft.
- Prüfe, ob `BACKEND_URL` mit `--dart-define` übergeben wird.
- Überprüfe, ob die API unter `/docs` antwortet.

### Probleme mit Datenbanken oder Migrationen

- Verwende `cd backend && alembic upgrade head`.
- Wenn du von SQLite auf MariaDB umstellst, überprüfe [docs/de/USO.md](docs/de/USO.md) und [docs/de/DATABASE.md](docs/de/DATABASE.md).

### Frontend mit Flutter-Fehlern

- Führe `cd frontend && flutter pub get` aus.
- Bei Problemen mit der Code-Generierung befolge die Dokumentation zu Hive und build_runner in [docs/de/ARQUITECTURA.md](docs/de/ARQUITECTURA.md).

## Beitragen

1. Forke das Repository.
2. Erstelle einen Branch (`git checkout -b feature/neue-funktion`).
3. Commite mit klaren, beschreibenden Nachrichten (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Pushe den Branch (`git push origin feature/neue-funktion`).
5. Öffne einen Pull Request mit Kontext, Änderungen und Validierung.

**Qualitätskonventionen:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` und `flutter test` müssen vor dem Merge bestehen.

## Lizenz

Dieses Projekt steht unter der **MIT-Lizenz**. Siehe [LICENSE](LICENSE).
