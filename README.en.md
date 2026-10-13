# Clakettes

The platform where film festivals live all year round: calls, short films, crews, venues and audience in one place.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Works on web, Android, iOS and desktop (Windows, macOS, Linux), in 9 languages and also offline.

---

## Who is it for?

- **Festivals**: publish your festival, open calls, receive short films, organize committees and juries, manage venues and share your awards.
- **Film professionals**: create your profile (directing, acting, sound, screenwriting, editing, wardrobe and more), showcase your awards and connect with festivals and crews.
- **Express crews**: coordinate your shooting group, geolocate participants and submit your short film to express contests.
- **Audience**: discover festivals, follow short films and contact the community.

## What you can do

- **Festivals and calls**: each festival can run several open calls with their own rules and registration forms.
- **Short films**: upload short films, link them to calls and shooting locations.
- **Profiles with awards**: awards linked to platform festivals or external via links, with field-by-field privacy control.
- **Chat**: direct and group or per-festival channel messages, with end-to-end encryption.
- **Maps**: venues and shooting locations on interactive maps, with opening in your favourite maps app.
- **Offline**: the app keeps working offline and syncs your changes when the connection returns.
- **In your language**: Spanish, English, French, German, Italian, Catalan, Basque, Galician and Occitan, with automatic detection.

## Requirements and startup

### Minimum requirements

- Python 3.12+
- Flutter SDK >= 3.0.0 and < 4.0.0
- Git
- Docker and Docker Compose for deployment/production environment
- Web-capable browser (Chrome/Brave recommended)

### Quick start

On Windows:

```bat
start.bat --dev
```

In PowerShell:

```powershell
./start.ps1 --dev
```

On Linux/macOS:

```bash
./start.sh --dev
```

This starts the backend at `http://localhost:8000` and the app in local mode; the API exposes Swagger/OpenAPI at `/docs`. You can disable either side with `--no-backend` or `--no-frontend`.

### Other useful options

```bash
start.bat --help
start.bat --migrate
start.bat --build
start.bat --build-all
```

See the full startup and deployment reference in [docs/en/HERRAMIENTAS.md](docs/en/HERRAMIENTAS.md) and [docs/en/USO.md](docs/en/USO.md).

## Environment variables and configuration

### Backend

Create or adjust `backend/.env` with at least:

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
```

MariaDB is used for production; scripts and deployment docs manage it with Docker.

### Frontend

The app reuses the backend by URL, normally with `--dart-define`:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

The project autostart already sets this up when `start.*` is used.

## Project status

🚧 **In active development** — Festivals, short films, chat with E2EE, maps, offline mode and 9 languages working; with backend (~1400) and frontend (69 files) tests.

**Upcoming roadmap:**

- [ ] Push notifications (Firebase/APNs)
- [ ] Signed Linux AppImage
- [ ] Windows MSI installer
- [x] Exportable OpenAPI API documentation (`/openapi.json` without duplicate operationIds + regenerated `docs/en/API.md`)

## Project documentation

The documentation map is in [docs/en/README.md](docs/en/README.md). It is the best entry point for each user type:

- [docs/en/USO.md](docs/en/USO.md): startup, operation, environment and daily use
- [docs/en/ADMINISTRACION.md](docs/en/ADMINISTRACION.md): administration, accounts and deployment
- [docs/en/INFRAESTRUCTURA.md](docs/en/INFRAESTRUCTURA.md): Docker, ports, CI and infra
- [docs/en/SEGURIDAD.md](docs/en/SEGURIDAD.md): tokens, policies and production checklist
- [docs/en/ARQUITECTURA.md](docs/en/ARQUITECTURA.md): backend/frontend architecture and key flows
- [docs/en/API.md](docs/en/API.md): endpoint reference
- [docs/en/DESARROLLO.md](docs/en/DESARROLLO.md): how to add endpoints or screens
- [docs/en/BACKEND.md](docs/en/BACKEND.md): backend guide (layers, config, auth, tests)
- [docs/en/DATABASE.md](docs/en/DATABASE.md): schema and migrations

Also, the starting point for development and project conventions is [AGENTS.md](AGENTS.md).

### See also

- [docs/en/README.md](docs/en/README.md): general index by audience
- [docs/en/HERRAMIENTAS.md](docs/en/HERRAMIENTAS.md): build, test and startup commands
- [docs/en/FUNCIONAL.md](docs/en/FUNCIONAL.md): real product use by role

### Quick FAQ

- **Do I need Docker to start?** No. Local startup with `start.*` works without Docker; Docker is for production environment and reproducible builds.
- **What do I do if the API does not respond?** Check that the backend is running at `http://localhost:8000` and that `/docs` responds.
- **Which document should I read first?** If you are a user, [docs/en/USO.md](docs/en/USO.md); if you are a developer, [docs/en/ARQUITECTURA.md](docs/en/ARQUITECTURA.md).
- **How do I know if a change requires documentation updates?** If it changes startup, API, roles, permissions, environment variables or schema, also update the matching documentation.

## For developers

> Full details in [`AGENTS.md`](AGENTS.md) (architecture, commands and conventions) and in the [`docs/`](docs/en/README.md) index (guides by role: functional, usage, administration, infrastructure, security, architecture, API).

**At a glance**: layered FastAPI backend (routers → services → SQLAlchemy models, SQLite in dev / MariaDB in prod, JWT + refresh, 18 Alembic migrations); Flutter Material 3 frontend with dark mode (singletons + `setState()` + streams, Hive offline, 24 reusable widgets).

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

## Local development

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

Backend + frontend (nginx) + MariaDB. Distributed builds (web, Windows, Linux, Android) are managed with `start.bat --build-all` and the script set in [docs/en/HERRAMIENTAS.md](docs/en/HERRAMIENTAS.md).

## Troubleshooting

### The backend does not start

- Verify Python 3.12+ is installed.
- Check that `backend/.env` exists and is valid.
- Run `cd backend && python -m uvicorn app.main:app --reload` to see the real error.

### The app does not connect to the API

- Make sure the backend is at `http://localhost:8000`.
- Check whether `BACKEND_URL` is being passed with `--dart-define`.
- Check that the API responds at `/docs`.

### Database or migration issues

- Use `cd backend && alembic upgrade head`.
- If switching from SQLite to MariaDB, see [docs/en/USO.md](docs/en/USO.md) and [docs/en/DATABASE.md](docs/en/DATABASE.md).

### Frontend with Flutter errors

- Run `cd frontend && flutter pub get`.
- For code-generation issues, follow the Hive and build_runner docs in [docs/en/ARQUITECTURA.md](docs/en/ARQUITECTURA.md).

## Contributing

1. Fork the repository.
2. Create a branch (`git checkout -b feature/nueva-funcionalidad`).
3. Commit with clear descriptive messages (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Push the branch (`git push origin feature/nueva-funcionalidad`).
5. Open a Pull Request with context, changes and validation.

**Quality conventions:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` and `flutter test` must pass before merging.

## License

This project is under the **MIT License**. See [LICENSE](LICENSE).
