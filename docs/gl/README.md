# Documentación — Clakettes

Toda a documentación existe nas 9 linguas da plataforma. O español é canónico:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](README.md) · [OC](../oc/README.md)

Este índice é a entrada principal da documentación do proxecto. Está pensado para que un usuario, un administrador ou un desenvolvedor atope a guía correcta sen ler arquivos ao azar.

## Como navegar pola documentación

- **Quero usar a app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Administro un despregamento** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Desenvolvemento** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md)
- **IA / axente** → [ARQUITECTURA.md](ARQUITECTURA.md) e o documento da tarefa; os comandos e convencións obrigatorias están en [../AGENTS.md](../../AGENTS.md)

## Principios da documentación

- **Un só documento canónico por tema**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) e [API.md](API.md) son a referencia oficial do seu ámbito.
- **Documentación por audiencia**: cada guía está escrita para un tipo de lector, non para un só conxunto de comandos.
- **Ligazóns directas**: desde aquí pódese chegar ao contido relevante en menos dun clic.
- **Sen duplicación innecesaria**: os documentos secundarios ligan ao canónico no canto de repetilo.

## Índice por documento

| Documento | Qué cubre | Audiencia |
|---|---|---|
| [FUNCIONAL.md](../es/FUNCIONAL.md) | Utilidad real por rol y flujos (festival, inscripción, comités, premios, chat/E2EE) | usuario, admin, IA |
| [USO.md](../es/USO.md) | Arranque, variables, migración SQLite↔MariaDB, backups, roles y operación | usuario, admin |
| [ADMINISTRACION.md](../es/ADMINISTRACION.md) | Endpoints `/api/admin`, cuenta inicial, rotación de secretos, límites, troubleshooting | admin |
| [INFRAESTRUCTURA.md](../es/INFRAESTRUCTURA.md) | Perfiles Docker, puertos, volúmenes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](../es/SEGURIDAD.md) | Tokens, matriz `require_*`, perímetro, checklist producción | admin, dev |
| [ARQUITECTURA.md](../es/ARQUITECTURA.md) | Mapa sistema + reglas backend/frontend + flujos clave | dev, IA |
| [API.md](../es/API.md) | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.md](../es/DESARROLLO.md) | Convención para añadir endpoint/pantalla + puertas CI | dev, IA |
| [HERRAMIENTAS.md](../es/HERRAMIENTAS.md) | Scripts `start.*`, builds distribuibles, Docker, fixes CI | dev |
| [PUSH.md](../es/PUSH.md) | Decisión de notificaciones sin Firebase | dev |
| [DATABASE.md](../es/DATABASE.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| [BACKEND.md](../es/BACKEND.md) | Guía del backend (capas, config, auth, tests) | dev |
| [AUDITORIA.md](../es/AUDITORIA.md) | Informe de auditoría (rev. 10/10/2026) | referencia |

## Ruta recomendada por perfil

### Usuario final

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) só se necesitan revisar permisos ou entorno produtivo

### Administrador de despregamento

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Desenvolvedor

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.md](API.md)
5. [DATABASE.md](DATABASE.md)

## Convencións para manter a documentación

- Actualiza o documento canónico antes que calquera resumo ou índice.
- Se cambias un fluxo de arranque, sincroniza [README.md](../../README.gl.md), [USO.md](USO.md) e [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Se cambias unha API pública, actualiza [API.md](API.md) e, se procede, [DESARROLLO.md](DESARROLLO.md).
- Se cambias o esquema ou a persistencia, revisa [DATABASE.md](DATABASE.md) e as migracións.

## FAQ rápida

- **Por onde empezo?** Le [USO.md](USO.md) se vas operar a app; le [ARQUITECTURA.md](ARQUITECTURA.md) se vas desenvolver.
- **Que é canónico e que non?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) e [DATABASE.md](DATABASE.md) son a referencia oficial para eses temas.
- **Onde atopo un comando ou script?** Revisa [HERRAMIENTAS.md](HERRAMIENTAS.md) e [../README.md](../../README.gl.md).
- **Como sei se un cambio require documentación?** Se afecta arranque, permisos, infraestrutura, API, ou modelo de datos, debe reflectirse na documentación pertinente.

## Ver tamén

- [../README.md](../../README.gl.md): vista xeral do proxecto
- [USO.md](USO.md): operación e configuración local
- [ADMINISTRACION.md](ADMINISTRACION.md): ámbito de despregamento e administración
- [ARQUITECTURA.md](ARQUITECTURA.md): mapa técnico do sistema
- [API.md](API.md): referencia de endpoints

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

A referencia completa de comandos e perfís do proxecto está en [HERRAMIENTAS.md](HERRAMIENTAS.md) e en [../README.md](../../README.gl.md).
