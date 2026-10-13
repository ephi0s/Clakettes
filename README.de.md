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

🚧 **In aktiver Entwicklung** — Festivals, Kurzfilme, Chat mit E2EE, Karten, Offline-Modus und 9 Sprachen lauffähig; mit Backend-Tests (~1400) und Frontend (69 Dateien).

**Nächste Roadmap:**

- [ ] Notificaciones push (Firebase/APNs)
- [ ] AppImage Linux firmado
- [ ] Windows MSI installer
- [x] Documentación API OpenAPI exportable (`/openapi.json` sin operationIds duplicados + `docs/de/API.md` regenerado)

## Projektdokumentation

Die Dok-Landkarte liegt in [docs/de/README.md](docs/de/README.md). Sie ist der beste Einstieg für jeden Nutzertyp:

- [docs/de/USO.md](docs/de/USO.md): arranque, operación, entorno y uso diario
- [docs/de/ADMINISTRACION.md](docs/de/ADMINISTRACION.md): administración, cuentas y despliegue
- [docs/de/INFRAESTRUCTURA.md](docs/de/INFRAESTRUCTURA.md): Docker, puertos, CI y infra
- [docs/de/SEGURIDAD.md](docs/de/SEGURIDAD.md): tokens, políticas y checklist de producción
- [docs/de/ARQUITECTURA.md](docs/de/ARQUITECTURA.md): arquitectura backend/frontend y flujos clave
- [docs/de/API.md](docs/de/API.md): referencia de endpoints
- [docs/de/DESARROLLO.md](docs/de/DESARROLLO.md): cómo añadir endpoints o pantallas
- [docs/de/BACKEND.md](docs/de/BACKEND.md): guía del backend (capas, config, auth, tests)
- [docs/de/DATABASE.md](docs/de/DATABASE.md): esquema y migraciones

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

**Auf einen Blick**: FastAPI-Backend in Schichten (Router → Dienste → SQLAlchemy-Modelle, SQLite in Dev / MariaDB in Prod, JWT + Refresh, 18 Alembic-Migrationen); Flutter-Frontend Material 3 mit Dark Mode (Singletons + `setState()` + Streams, Hive offline, 24 wiederverwendbare Widgets).

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

- Verifica que Python 3.12+ esté instalado.
- Comprueba que `backend/.env` existe y es válido.
- Ejecuta `cd backend && python -m uvicorn app.main:app --reload` para ver el error real.

### Die App verbindet nicht mit der API

- Asegúrate de que el backend está en `http://localhost:8000`.
- Revisa si `BACKEND_URL` se está pasando con `--dart-define`.
- Comprueba que la API responde en `/docs`.

### Probleme mit Datenbanken oder Migrationen

- Usa `cd backend && alembic upgrade head`.
- Si cambias de SQLite a MariaDB, revisa [docs/de/USO.md](docs/de/USO.md) y [docs/de/DATABASE.md](docs/de/DATABASE.md).

### Frontend mit Flutter-Fehlern

- Ejecuta `cd frontend && flutter pub get`.
- Si hay problemas de generación de código, sigue la documentación de Hive y build_runner en [docs/de/ARQUITECTURA.md](docs/de/ARQUITECTURA.md).

## Beitragen

1. Haz un fork del repositorio.
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`).
3. Haz commit con mensajes claros y descriptivos (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Empuja la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request con contexto, cambios y validación.

**Qualitätskonventionen:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` y `flutter test` müssen vor dem Merge bestehen.

## Lizenz

Dieses Projekt steht unter der **MIT-Lizenz**. Siehe [LICENSE](LICENSE).
