---
name: docker-devops-expert
description: Expert guidance for Clakettes Docker, CI/CD, and deployment. Covers docker-compose profiles (dev/db/prod), multi-stage Dockerfiles, port mapping (8000/3000/3306/80), GitHub Actions CI, GitLab CI, build-all script, and CHROME_EXECUTABLE detection for Flutter web. Use when working with Docker, CI pipelines, or deployment workflows.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 23 Jun 2026 01:43:00 GMT
---
# Docker/DevOps Expert

## Docker Compose

`docker-compose.yml` defines 3 profiles:

### Dev (default: `docker compose up`)
- `backend` (target: dev): port `${PORT_BACKEND:-8000}:8000`, volume-mounts `./backend:/app`, `backend-data:/app/data`
- `frontend` (target: dev): port `${PORT_FRONTEND:-3000}:3000`, volume-mounts `./frontend:/app`, `depends_on: backend`
- Backend env: `DATABASE_URL` (default `sqlite:///./data/clakettes.db`), `SECRET_KEY` (default `dev-secret-change-in-production`)

### DB (`docker compose --profile db up`)
- MariaDB 11, port `${PORT_DB:-3306}:3306`
- Healthcheck: `healthcheck.sh --connect --innodb_initialized`
- Credentials: user `clakettes_user`, password `clakettes_password`, DB `clakettes_db`

### Prod (`docker compose --profile prod up -d`)
- `backend-prod` (target: prod): connects to MariaDB via `db` hostname, `SECRET_KEY:?error` (required)
- `frontend-prod` (target: prod): nginx on port `${PORT_FRONTEND_PROD:-80}`
- `db`: same MariaDB service, shared across profiles

## Dockerfiles

### Backend (`backend/Dockerfile`)
- Base: `python:3.12-slim-bookworm`
- **dev target**: `uvicorn app.main:app --reload`
- **prod target**: non-root `appuser`, no reload

### Frontend (`frontend/Dockerfile`)
- Base: `ubuntu:24.04`, installs Flutter 3.24.0 from git
- **dev target**: `flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=$BACKEND_URL`
- **build target**: `flutter build web --release`
- **prod target**: nginx:alpine serving built web, port 80
- `BACKEND_URL` build arg for all targets

## CI

### GitHub Actions (`.github/workflows/ci.yml`)
- Triggers: push `main`/`develop`, PRs to `main`
- Parallel jobs: (1) backend (Python 3.12, ruff → pytest), (2) frontend (Flutter 3.24, analyze → test), (3) docker-build (needs 1+2, Buildx, layer caching)

### GitLab CI (`.gitlab-ci.yml`)
- Stages: lint → test → build
- Parallel lint: ruff + flutter analyze
- Parallel test: pytest + flutter test
- Docker build on main only, pushes to GitLab container registry

## Env & Ports

Defaults: Backend 8000, Frontend dev 3000, Frontend prod 80, MariaDB 3306. Scripts find next free port from 60000 if occupied.

Key vars: `PORT_BACKEND`, `PORT_FRONTEND`, `PORT_FRONTEND_PROD`, `PORT_DB`, `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, `BACKEND_URL`, `MARIADB_*`.

## CHROME_EXECUTABLE

Auto-detection order: Brave Beta → Brave Stable → Chrome (Program Files, Program Files (x86), Local AppData).
