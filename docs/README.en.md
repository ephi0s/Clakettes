# Documentation — Clakettes

All documentation exists in the platform's 9 languages. Spanish is canonical:
[Español](README.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Italiano](README.it.md) · [Català](README.ca.md) · [Euskara](README.eu.md) · [Galego](README.gl.md) · [Occitan](README.oc.md).

This index is the main entry point to the project documentation. It is designed so a user, an administrator or a developer finds the right guide without reading files at random.

## How to navigate the documentation

- **I want to use the app** → [USO.md](USO.en.md) + [FUNCIONAL.md](FUNCIONAL.en.md)
- **I manage a deployment** → [ADMINISTRACION.md](ADMINISTRACION.en.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.en.md) + [SEGURIDAD.md](SEGURIDAD.en.md)
- **Development** → [ARQUITECTURA.md](ARQUITECTURA.en.md) + [DESARROLLO.md](DESARROLLO.en.md) + [API.md](API.md) + [DATABASE.md](DATABASE.en.md)
- **AI / agent** → [ARQUITECTURA.md](ARQUITECTURA.en.md) and the task document; mandatory commands and conventions are in [../AGENTS.md](../AGENTS.md)

## Documentation principles

- **One canonical document per topic**: [SEGURIDAD.md](SEGURIDAD.en.md), [USO.md](USO.en.md), [DATABASE.md](DATABASE.en.md) and [API.md](API.md) are the official reference for their scope.
- **Audience-based documentation**: each guide is written for one reader type, not for a single command set.
- **Direct links**: from here the relevant content is less than one click away.
- **No unnecessary duplication**: secondary documents link to the canonical one instead of repeating it.

## Document index

| Document | What it covers | Audience |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.en.md) | Real value by role and flows (festival, registration, committees, awards, chat/E2EE) | user, admin, AI |
| [USO.md](USO.en.md) | Startup, variables, SQLite↔MariaDB migration, backups, roles and operation | user, admin |
| [ADMINISTRACION.md](ADMINISTRACION.en.md) | `/api/admin` endpoints, initial account, secret rotation, limits, troubleshooting | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.en.md) | Docker profiles, ports, volumes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.en.md) | Tokens, `require_*` matrix, perimeter, production checklist | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.en.md) | System map + backend/frontend rules + key flows | dev, AI |
| [API.md](API.md) | Endpoint reference (regenerable with `tools/gen_api.py`) | dev, AI |
| [DESARROLLO.md](DESARROLLO.en.md) | Convention for adding endpoint/screen + CI gates | dev, AI |
| [HERRAMIENTAS.md](HERRAMIENTAS.en.md) | `start.*` scripts, distributable builds, Docker, CI fixes | dev |
| [PUSH.md](PUSH.en.md) | Notification decision without Firebase | dev |
| [DATABASE.md](DATABASE.en.md) | Dual SQLite/MariaDB schema, per-model cards, ER | dev, AI |
| [BACKEND.md](BACKEND.en.md) | Backend guide (layers, config, auth, tests) | dev |
| [AUDITORIA.md](AUDITORIA.en.md) | Audit report (rev. 10/10/2026) | reference |

## Recommended path by profile

### End user

1. [USO.md](USO.en.md)
2. [FUNCIONAL.md](FUNCIONAL.en.md)
3. [SEGURIDAD.md](SEGURIDAD.en.md) only if they need to review permissions or the production environment

### Deployment administrator

1. [ADMINISTRACION.md](ADMINISTRACION.en.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.en.md)
3. [SEGURIDAD.md](SEGURIDAD.en.md)
4. [USO.md](USO.en.md)

### Developer

1. [../AGENTS.md](../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.en.md)
3. [DESARROLLO.md](DESARROLLO.en.md)
4. [API.md](API.md)
5. [DATABASE.md](DATABASE.en.md)

## Conventions for maintaining documentation

- Update the canonical document before any summary or index.
- If you change a startup flow, sync [README.md](../README.en.md), [USO.md](USO.en.md) and [HERRAMIENTAS.md](HERRAMIENTAS.en.md).
- If you change a public API, update [API.md](API.md) and, where applicable, [DESARROLLO.md](DESARROLLO.en.md).
- If you change the schema or persistence, review [DATABASE.md](DATABASE.en.md) and migrations.

## Quick FAQ

- **Where do I start?** Read [USO.md](USO.en.md) if you will operate the app; read [ARQUITECTURA.md](ARQUITECTURA.en.md) if you will develop.
- **What is canonical and what is not?** [USO.md](USO.en.md), [SEGURIDAD.md](SEGURIDAD.en.md), [API.md](API.md) and [DATABASE.md](DATABASE.en.md) are the official reference for those topics.
- **Where do I find a command or script?** Check [HERRAMIENTAS.md](HERRAMIENTAS.en.md) and [../README.md](../README.en.md).
- **How do I know if a change needs documentation?** If it affects startup, permissions, infrastructure, API, or data model, it must be reflected in the relevant documentation.

## See also

- [../README.md](../README.en.md): project overview
- [USO.md](USO.en.md): local operation and configuration
- [ADMINISTRACION.md](ADMINISTRACION.en.md): deployment and administration scope
- [ARQUITECTURA.md](ARQUITECTURA.en.md): technical system map
- [API.md](API.md): endpoint reference

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

The full command and profile reference is in [HERRAMIENTAS.md](HERRAMIENTAS.en.md) and in [../README.md](../README.en.md).
