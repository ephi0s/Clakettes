# Documentation — Clakettes

All documentation exists in the platform's 9 languages. Spanish is canonical:
[ES](../es/README.md) · [EN](README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

This index is the main entry point to the project documentation. It is designed so a user, an administrator or a developer finds the right guide without reading files at random.

## How to navigate the documentation

- **I want to use the app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **I manage a deployment** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Development** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](../es/API.md) + [DATABASE.md](DATABASE.md)
- **AI / agent** → [ARQUITECTURA.md](ARQUITECTURA.md) and the task document; mandatory commands and conventions are in [../AGENTS.md](../../AGENTS.md)

## Documentation principles

- **One canonical document per topic**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) and [API.md](../es/API.md) are the official reference for their scope.
- **Audience-based documentation**: each guide is written for one reader type, not for a single command set.
- **Direct links**: from here the relevant content is less than one click away.
- **No unnecessary duplication**: secondary documents link to the canonical one instead of repeating it.

## Document index

| Document | What it covers | Audience |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Real value by role and flows (festival, registration, committees, awards, chat/E2EE) | user, admin, AI |
| [USO.md](USO.md) | Startup, variables, SQLite↔MariaDB migration, backups, roles and operation | user, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | `/api/admin` endpoints, initial account, secret rotation, limits, troubleshooting | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Docker profiles, ports, volumes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, `require_*` matrix, perimeter, production checklist | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | System map + backend/frontend rules + key flows | dev, AI |
| [API.md](../es/API.md) | Endpoint reference (regenerable with `tools/gen_api.py`) | dev, AI |
| [DESARROLLO.md](DESARROLLO.md) | Convention for adding endpoint/screen + CI gates | dev, AI |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | `start.*` scripts, distributable builds, Docker, CI fixes | dev |
| [PUSH.md](PUSH.md) | Notification decision without Firebase | dev |
| [DATABASE.md](DATABASE.md) | Dual SQLite/MariaDB schema, per-model cards, ER | dev, AI |
| [BACKEND.md](BACKEND.md) | Backend guide (layers, config, auth, tests) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Audit report (rev. 10/10/2026) | reference |

## Recommended path by profile

### End user

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) only if they need to review permissions or the production environment

### Deployment administrator

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Developer

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.md](../es/API.md)
5. [DATABASE.md](DATABASE.md)

## Conventions for maintaining documentation

- Update the canonical document before any summary or index.
- If you change a startup flow, sync [README.md](../../README.en.md), [USO.md](USO.md) and [HERRAMIENTAS.md](HERRAMIENTAS.md).
- If you change a public API, update [API.md](../es/API.md) and, where applicable, [DESARROLLO.md](DESARROLLO.md).
- If you change the schema or persistence, review [DATABASE.md](DATABASE.md) and migrations.

## Quick FAQ

- **Where do I start?** Read [USO.md](USO.md) if you will operate the app; read [ARQUITECTURA.md](ARQUITECTURA.md) if you will develop.
- **What is canonical and what is not?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](../es/API.md) and [DATABASE.md](DATABASE.md) are the official reference for those topics.
- **Where do I find a command or script?** Check [HERRAMIENTAS.md](HERRAMIENTAS.md) and [../README.md](../../README.en.md).
- **How do I know if a change needs documentation?** If it affects startup, permissions, infrastructure, API, or data model, it must be reflected in the relevant documentation.

## See also

- [../README.md](../../README.en.md): project overview
- [USO.md](USO.md): local operation and configuration
- [ADMINISTRACION.md](ADMINISTRACION.md): deployment and administration scope
- [ARQUITECTURA.md](ARQUITECTURA.md): technical system map
- [API.md](../es/API.md): endpoint reference

## Recommended start

To start in a local environment:

```bash
cd backend && python -m uvicorn app.main:app --reload
cd frontend && flutter run
```

Or, using the project scripts:

```bat
start.bat --dev
```

The full command and profile reference is in [HERRAMIENTAS.md](HERRAMIENTAS.md) and in [../README.md](../../README.en.md).
