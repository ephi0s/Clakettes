# Documentación — Clakettes

Mapa por audiencia. La IA debe empezar por `ARQUITECTURA.md` y el doc de su tarea; los humanos por su rol.

## Según tu rol

- **Quiero usar la app** → `USO.md` (arranque, configuración, operación) + `FUNCIONAL.md` (qué hacer según tu rol: festival, profesional, equipo, público)
- **Administro un despliegue** → `ADMINISTRACION.md` (cuentas, backups, secretos, troubleshooting) + `INFRAESTRUCTURA.md` (Docker, puertos, entorno, CI) + `SEGURIDAD.md` (checklist prod)
- **Desarrollo** → `ARQUITECTURA.md` (mapa + reglas) + `DESARROLLO.md` (cómo añadir endpoint/pantalla) + `API.md` (referencia de endpoints) + `../backend/DATABASE.md` (esquema)
- **IA / agente** → `ARQUITECTURA.md` primero; luego el doc de la tarea. Comandos y convenciones vinculantes en `../AGENTS.md`

## Índice

| Doc | Qué cubre | Audiencia |
|---|---|---|
| `FUNCIONAL.md` | Utilidad real por rol y flujos (festival, inscripción, comités, premios, chat/E2EE) | usuario, admin, IA |
| `USO.md` | Arranque, variables, migración SQLite↔MariaDB, backups, roles (resumen) | usuario, admin |
| `ADMINISTRACION.md` | Endpoints `/api/admin`, cuenta inicial, rotación de secretos, límites, troubleshooting | admin |
| `INFRAESTRUCTURA.md` | Perfiles Docker, puertos, volúmenes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| `SEGURIDAD.md` | Tokens, matriz `require_*`, perímetro, checklist producción | admin, dev |
| `ARQUITECTURA.md` | Mapa sistema + reglas backend/frontend + flujos clave | dev, IA |
| `API.md` | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| `DESARROLLO.md` | Convención para añadir endpoint/pantalla + puertas CI | dev, IA |
| `HERRAMIENTAS.md` | Scripts `start.*`, builds distribuibles, Docker, fixes CI | dev |
| `PUSH.md` | Decisión de notificaciones sin Firebase | dev |
| `../backend/DATABASE.md` | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| `../backend/BACKEND.md` | Guía del backend (capas, config, auth, tests) | dev |
| `AUDITORIA.md` | Informe histórico 09/10/2026 (no mantener) | referencia |

Regla: `SEGURIDAD.md`, `USO.md`, `../backend/DATABASE.md` y `API.md` son canónicos en su tema; el resto los referencia sin duplicar.
