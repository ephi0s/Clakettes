# Clakettes

The platform where film festivals live all year: calls, shorts, teams, venues and audience in one place.

[![MIT License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20languages-blue)](frontend/assets/l10n/)

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

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
- **Offline**: the app keeps working offline, stores each node's origin in the cache and syncs your changes when back online.
- **Federation**: trusted nodes with mTLS, identity portability, chat and events between nodes, moderation, metrics and resilience.
- **In your language**: Spanish, English, French, German, Italian, Catalan, Basque, Galician and Occitan (823 keys per language), with automatic OS locale detection.

## Requirements and startup

### Minimum requirements

- Python 3.12+
- Flutter SDK >= 3.0.0 and < 4.0.0
- Git
- Docker and Docker Compose for deployment/production environment
- Browser with web support (Chrome/Brave recommended)

### Quick start

In PowerShell:

```powershell
./start.ps1 --dev
```

On Linux/macOS:

```bash
./start.sh --dev
```

This starts the backend at `http://localhost:8000` and the app locally; the API exposes Swagger/OpenAPI at `/docs`. You can disable either part with `--no-backend` or `--no-frontend`.

## Environment variables and configuration

### Backend

Create or adjust `backend/.env` with at least:

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=your-secret-key
CORS_ORIGINS=https://your-domain.com
APP_ENV=development
PUBLIC_BASE_URL=https://your-domain.com
# Federation with mTLS (production)
MTLS_REQUIRED=false
MTLS_CA_BUNDLE_PATH=
MTLS_CLIENT_CERT_PATH=
MTLS_CLIENT_KEY_PATH=
# Payments (mock by default; Stripe/Redsys on demand)
PAYMENTS_PROVIDER=mock
```

For production, MariaDB is used; scripts and deployment docs manage it with Docker.

### Frontend

The app reuses the backend by URL, usually with `--dart-define`:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

The project's automatic startup configures this when using `start.*`.

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
- [docs/en/FEDERATION_PROTOCOL.md](docs/en/FEDERATION_PROTOCOL.md): protocol between nodes (phases 2-10)
- [docs/en/FEDERATION_SECURITY.md](docs/en/FEDERATION_SECURITY.md): trust, mTLS, portability and resilience
- [docs/en/FEDERATION_SCHEMA.md](docs/en/FEDERATION_SCHEMA.md): federated entities and checksum
- [docs/en/FEDERATION_CHAT_BROKER.md](docs/en/FEDERATION_CHAT_BROKER.md): transport decision and implemented status

Also, the starting point for development and project convention is [AGENTS.md](AGENTS.md).

### See also

- [docs/en/README.md](docs/en/README.md): general index by audience
- [docs/en/HERRAMIENTAS.md](docs/en/HERRAMIENTAS.md): build, test and startup commands
- [docs/en/FUNCIONAL.md](docs/en/FUNCIONAL.md): real product usage by role

### Quick FAQ

- **Do I need Docker to start?** No. Local startup with `start.*` works without Docker; Docker is for production environment and reproducible builds.
- **What if the API doesn't respond?** Check that the backend is running at `http://localhost:8000` and that `/docs` responds.
- **Which document should I read first?** If you are a user, [docs/en/USO.md](docs/en/USO.md); if you are a developer, [docs/en/ARQUITECTURA.md](docs/en/ARQUITECTURA.md).
- **How do I know if a change requires updating documentation?** If startup, API, roles, permissions, environment variables or schema change, update the corresponding documentation too.

## Contributing

1. Fork the repository.
2. Create a branch (`git checkout -b feature/new-feature`).
3. Commit with clear, descriptive messages (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Push the branch (`git push origin feature/new-feature`).
5. Open a Pull Request with context, changes and validation.

**Quality conventions:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` and `flutter test` must pass before merging. GitHub Actions runs these gates in parallel and Dependabot opens grouped weekly PRs: patch/minor merge themselves with green CI, major stays for manual review (detail in [docs/en/INFRAESTRUCTURA.md](docs/en/INFRAESTRUCTURA.md)).

## License

This project is under the **MIT License**. See [LICENSE](LICENSE).