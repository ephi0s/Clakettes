# Clakettes

The platform where film festivals live all year: calls, shorts, teams, venues and audience in one place.

[![MIT License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20languages-blue)](frontend/assets/l10n/)

Works on web, Android, iOS and desktop (Windows, macOS, Linux), in 9 languages and offline too.

---

## Who is it for?

- **Festivals**: publish your festival, open calls, receive shorts, organize committees and juries, manage venues and announce awards.
- **Film professionals**: create your profile (directing, acting, sound, writing, editing, costume and more), show your awards and connect with festivals and teams.
- **Express teams**: coordinate your shoot group, geolocate participants and submit your short to express contests.
- **Audience**: discover festivals, follow shorts and contact the community.

## What you can do

- **Festivals and calls**: each festival can have multiple open calls with their own rules and registration forms.
- **Shorts**: upload short films, link them to calls and shooting locations.
- **Profiles with awards**: awards linked to platform festivals or external via links, with field-by-field privacy control.
- **Chat**: direct and group/channel messages per festival, with end-to-end encryption.
- **Maps**: venues and shooting locations on interactive maps, open in your favorite maps app.
- **Offline**: the app keeps working offline and syncs your changes when back online.
- **In your language**: Spanish, English, French, German, Italian, Catalan, Basque, Galician and Occitan, with auto-detection.

## Requirements and startup

### Minimum requirements

- Python 3.12+
- Flutter SDK >= 3.0.0 and < 4.0.0
- Git
- Docker and Docker Compose for deployment/production environment
- Browser with web support (Chrome/Brave recommended)

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

This starts the backend at `http://localhost:8000` and the app locally; the API exposes Swagger/OpenAPI at `/docs`. You can disable either part with `--no-backend` or `--no-frontend`.

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
SECRET_KEY=your-secret-key
CORS_ORIGINS=https://your-domain.com
```

For production, MariaDB is used; scripts and deployment docs manage it with Docker.

### Frontend

The app reuses the backend by URL, usually with `--dart-define`:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

The project's automatic startup configures this when using `start.*`.

## Project status

🚧 **Active development** — Festivals, shorts, E2EE chat, maps, offline mode and 9 languages working; with backend tests (~1400) and frontend (75 test files).

**Next roadmap:**

- [ ] Push notifications (Firebase/APNs)
- [ ] Signed Linux AppImage
- [ ] Windows MSI installer
- [x] Exportable OpenAPI documentation (`/openapi.json` without duplicate operationIds + regenerated `docs/en/API.md`)

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
- [docs/en/FEDERATION_PROTOCOL.md](docs/en/FEDERATION_PROTOCOL.md): federation protocol (phase 4)
- [docs/en/FEDERATION_SCHEMA.md](docs/en/FEDERATION_SCHEMA.md): Clakettes Schema v1
- [docs/en/FEDERATION_SECURITY.md](docs/en/FEDERATION_SECURITY.md): federated trust model
- [docs/en/PUSH.md](docs/en/PUSH.md): push notification decision

Also, the starting point for development and project convention is [AGENTS.md](AGENTS.md).

### See also

- [docs/en/README.md](docs/en/README.md): general index by audience
- [docs/en/HERRAMIENTAS.md](docs/en/HERRAMIENTAS.md): build, test and startup commands
- [docs/en/FUNCIONAL.md](docs/en/FUNCIONAL.md): real product usage by role
- [docs/en/PUSH.md](docs/en/PUSH.md): push notification decision

### Quick FAQ

- **Do I need Docker to start?** No. Local startup with `start.*` works without Docker; Docker is for production environment and reproducible builds.
- **What if the API doesn't respond?** Check that the backend is running at `http://localhost:8000` and that `/docs` responds.
- **Which document should I read first?** If you are a user, [docs/en/USO.md](docs/en/USO.md); if you are a developer, [docs/en/ARQUITECTURA.md](docs/en/ARQUITECTURA.md).
- **How do I know if a change requires updating documentation?** If startup, API, roles, permissions, environment variables or schema change, update the corresponding documentation too.

## For developers

> Full detail in [`AGENTS.md`](AGENTS.md) (architecture, commands and conventions) and in the [`docs/`](docs/en/README.md) index (guides by role: functional, usage, administration, infrastructure, security, architecture, API).

**At a glance**: layered FastAPI backend (routers → SQLAlchemy services → models, SQLite in dev / MariaDB in prod, JWT + refresh, 36 Alembic migrations); Flutter Material 3 frontend with dark mode (singletons + `setState()` + streams, Hive offline, 32 reusable widgets).

```bash
# Tests
cd backend && python -m pytest tests/ -x -q --tb=short
cd frontend && flutter test

# Lint
cd backend && ruff check . && ruff format --check .
cd frontend && flutter analyze

# Migrations
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

### Backend won't start

- Verify Python 3.12+ is installed.
- Check that `backend/.env` exists and is valid.
- Run `cd backend && python -m uvicorn app.main:app --reload` to see the real error.

### App doesn't connect to the API

- Make sure the backend is at `http://localhost:8000`.
- Check whether `BACKEND_URL` is passed with `--dart-define`.
- Verify the API responds at `/docs`.

### Database or migration problems

- Use `cd backend && alembic upgrade head`.
- If switching from SQLite to MariaDB, review [docs/en/USO.md](docs/en/USO.md) and [docs/en/DATABASE.md](docs/en/DATABASE.md).

### Frontend Flutter errors

- Run `cd frontend && flutter pub get`.
- If there are code generation issues, follow the Hive and build_runner documentation in [docs/en/ARQUITECTURA.md](docs/en/ARQUITECTURA.md).

## Contributing

1. Fork the repository.
2. Create a branch (`git checkout -b feature/new-feature`).
3. Commit with clear, descriptive messages (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Push the branch (`git push origin feature/new-feature`).
5. Open a Pull Request with context, changes and validation.

**Quality conventions:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` and `flutter test` must pass before merging.

## License

This project is under the **MIT License**. See [LICENSE](LICENSE).