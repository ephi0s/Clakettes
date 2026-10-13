# Documentación — Clakettes

Este índice es la entrada principal de la documentación del proyecto. Está pensado para que un usuario, un administrador o un desarrollador encuentre la guía correcta sin leer archivos al azar.

## Idiomas

Toda la documentación existe en las 9 lenguas de la plataforma. El español (canario) es el canónico:
[ES](README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

## Cómo navegar por la documentación

- **Quiero usar la app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Administro un despliegue** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Desarrollo** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md)
- **IA / agente** → [ARQUITECTURA.md](ARQUITECTURA.md) y el documento de la tarea; los comandos y convenciones obligatorias están en [../AGENTS.md](../../AGENTS.md)

## Principios de la documentación

- **Un solo documento canónico por tema**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) y [API.md](API.md) son la referencia oficial de su ámbito.
- **Documentación por audiencia**: cada guía está escrita para un tipo de lector, no para un solo conjunto de comandos.
- **Enlaces directos**: desde aquí se puede llegar al contenido relevante en menos de un clic.
- **Sin duplicación innecesaria**: los documentos secundarios enlazan al canónico en lugar de repetirlo.

## Índice por documento

| Documento | Qué cubre | Audiencia |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Utilidad real por rol y flujos (festival, inscripción, comités, premios, chat/E2EE) | usuario, admin, IA |
| [USO.md](USO.md) | Arranque, variables, migración SQLite↔MariaDB, backups, roles y operación | usuario, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoints `/api/admin`, cuenta inicial, rotación de secretos, límites, troubleshooting | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Perfiles Docker, puertos, volúmenes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, matriz `require_*`, perímetro, checklist producción | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Mapa sistema + reglas backend/frontend + flujos clave | dev, IA |
| [API.md](API.md) | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.md](DESARROLLO.md) | Convención para añadir endpoint/pantalla + puertas CI | dev, IA |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Scripts `start.*`, builds distribuibles, Docker, fixes CI | dev |
| [PUSH.md](PUSH.md) | Decisión de notificaciones sin Firebase | dev |
| [DATABASE.md](DATABASE.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| [BACKEND.md](BACKEND.md) | Guía del backend (capas, config, auth, tests) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Informe de auditoría (rev. 10/10/2026) | referencia |

## Ruta recomendada por perfil

### Usuario final

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) solo si necesitan revisar permisos o entorno productivo

### Administrador de despliegue

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Desarrollador

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.md](API.md)
5. [DATABASE.md](DATABASE.md)

## Convenciones para mantener la documentación

- Actualiza el documento canónico antes que cualquier resumen o índice.
- Si cambias un flujo de arranque, sincroniza [README.md](../../README.md), [USO.md](USO.md) y [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Si cambias una API pública, actualiza [API.md](API.md) y, si procede, [DESARROLLO.md](DESARROLLO.md).
- Si cambias el esquema o la persistencia, revisa [DATABASE.md](DATABASE.md) y las migraciones.

## FAQ rápida

- **¿Por dónde empiezo?** Lee [USO.md](USO.md) si vas a operar la app; lee [ARQUITECTURA.md](ARQUITECTURA.md) si vas a desarrollar.
- **¿Qué es canónico y qué no?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) y [DATABASE.md](DATABASE.md) son la referencia oficial para esos temas.
- **¿Dónde encuentro un comando o script?** Revisa [HERRAMIENTAS.md](HERRAMIENTAS.md) y [../README.md](../../README.md).
- **¿Cómo sé si un cambio requiere documentación?** Si afecta arranque, permisos, infraestructura, API, o modelo de datos, debe reflejarse en la documentación pertinente.

## Ver también

- [../README.md](../../README.md): vista general del proyecto
- [USO.md](USO.md): operación y configuración local
- [ADMINISTRACION.md](ADMINISTRACION.md): ámbito de despliegue y administración
- [ARQUITECTURA.md](ARQUITECTURA.md): mapa técnico del sistema
- [API.md](API.md): referencia de endpoints

## Inicio recomendado

Para empezar en un entorno local:

```bash
cd backend && python -m uvicorn app.main:app --reload
cd frontend && flutter run
```

O, usando los scripts del proyecto:

```bat
start.bat --dev
```

La referencia completa de comandos y perfiles del proyecto está en [HERRAMIENTAS.md](HERRAMIENTAS.md) y en [../README.md](../../README.md).
