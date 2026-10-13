# Documentación — Clakettes

Toda a documentación existe nas 9 linguas da plataforma. O español é canónico:
[Español](README.md) · [English](README.en.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Italiano](README.it.md) · [Català](README.ca.md) · [Euskara](README.eu.md) · [Occitan](README.oc.md).

Este índice é a entrada principal da documentación do proxecto. Está pensado para que un usuario, un administrador ou un desenvolvedor atope a guía correcta sen ler arquivos ao azar.

## Como navegar pola documentación

- **Quero usar a app** → [USO.md](USO.gl.md) + [FUNCIONAL.md](FUNCIONAL.gl.md)
- **Administro un despregamento** → [ADMINISTRACION.md](ADMINISTRACION.gl.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.gl.md) + [SEGURIDAD.md](SEGURIDAD.gl.md)
- **Desenvolvemento** → [ARQUITECTURA.md](ARQUITECTURA.gl.md) + [DESARROLLO.md](DESARROLLO.gl.md) + [API.md](API.gl.md) + [DATABASE.md](DATABASE.gl.md)
- **IA / axente** → [ARQUITECTURA.md](ARQUITECTURA.gl.md) e o documento da tarefa; os comandos e convencións obrigatorias están en [../AGENTS.md](../AGENTS.md)

## Principios da documentación

- **Un só documento canónico por tema**: [SEGURIDAD.md](SEGURIDAD.gl.md), [USO.md](USO.gl.md), [DATABASE.md](DATABASE.gl.md) e [API.md](API.gl.md) son a referencia oficial do seu ámbito.
- **Documentación por audiencia**: cada guía está escrita para un tipo de lector, non para un só conxunto de comandos.
- **Ligazóns directas**: desde aquí pódese chegar ao contido relevante en menos dun clic.
- **Sen duplicación innecesaria**: os documentos secundarios ligan ao canónico no canto de repetilo.

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

1. [USO.md](USO.gl.md)
2. [FUNCIONAL.md](FUNCIONAL.gl.md)
3. [SEGURIDAD.md](SEGURIDAD.gl.md) só se necesitan revisar permisos ou entorno produtivo

### Administrador de despregamento

1. [ADMINISTRACION.md](ADMINISTRACION.gl.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.gl.md)
3. [SEGURIDAD.md](SEGURIDAD.gl.md)
4. [USO.md](USO.gl.md)

### Desenvolvedor

1. [../AGENTS.md](../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.gl.md)
3. [DESARROLLO.md](DESARROLLO.gl.md)
4. [API.md](API.gl.md)
5. [DATABASE.md](DATABASE.gl.md)

## Convencións para manter a documentación

- Actualiza o documento canónico antes que calquera resumo ou índice.
- Se cambias un fluxo de arranque, sincroniza [README.md](../README.gl.md), [USO.md](USO.gl.md) e [HERRAMIENTAS.md](HERRAMIENTAS.gl.md).
- Se cambias unha API pública, actualiza [API.md](API.gl.md) e, se procede, [DESARROLLO.md](DESARROLLO.gl.md).
- Se cambias o esquema ou a persistencia, revisa [DATABASE.md](DATABASE.gl.md) e as migracións.

## FAQ rápida

- **Por onde empezo?** Le [USO.md](USO.gl.md) se vas operar a app; le [ARQUITECTURA.md](ARQUITECTURA.gl.md) se vas desenvolver.
- **Que é canónico e que non?** [USO.md](USO.gl.md), [SEGURIDAD.md](SEGURIDAD.gl.md), [API.md](API.gl.md) e [DATABASE.md](DATABASE.gl.md) son a referencia oficial para eses temas.
- **Onde atopo un comando ou script?** Revisa [HERRAMIENTAS.md](HERRAMIENTAS.gl.md) e [../README.md](../README.gl.md).
- **Como sei se un cambio require documentación?** Se afecta arranque, permisos, infraestrutura, API, ou modelo de datos, debe reflectirse na documentación pertinente.

## Ver tamén

- [../README.md](../README.gl.md): vista xeral do proxecto
- [USO.md](USO.gl.md): operación e configuración local
- [ADMINISTRACION.md](ADMINISTRACION.gl.md): ámbito de despregamento e administración
- [ARQUITECTURA.md](ARQUITECTURA.gl.md): mapa técnico do sistema
- [API.md](API.gl.md): referencia de endpoints

## Inicio recomendado

Para empezar nun entorno local:

```bash
cd backend && python -m uvicorn app.main:app --reload
cd frontend && flutter run
```

O, usando os scripts do proxecto:

```bat
start.bat --dev
```

A referencia completa de comandos e perfís do proxecto está en [HERRAMIENTAS.md](HERRAMIENTAS.gl.md) e en [../README.md](../README.gl.md).
