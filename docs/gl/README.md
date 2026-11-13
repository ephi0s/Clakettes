# Documentación — Clakettes

Este índice es a entrada principal da documentación do proxecto. Está pensado para que un usuario, un administrador ou un desenvolvedor atopa a guía correcta sen ler arquivos ao azar.

## Idiomas

Toda a documentación existe nas 9 linguas da plataforma. O español (canario) é o canónico:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](README.md) · [OC](../oc/README.md)

## Como navegar pola documentación

- **Quiero usar a app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Administro un despliegue** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Desenvolvo** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md) + [BACKEND.md](BACKEND.md)
- **IA / agente** → [ARQUITECTURA.md](ARQUITECTURA.md) e o documento da tarefa; os comandos e convencións obrigatorias están en [../AGENTS.md](../../AGENTS.md)

## Principios da documentación

- **Un so documento canónico por tema**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) e [API.md](API.md) son a referencia oficial do seu ámbito.
- **Documentación por audiencia**: cada guía está escrita para un tipo de lector, non para un so conxunto de comandos.
- **Enlaces directos**: desde aquí se pode chegar ao contido relevante en menos dun clic.
- **Sen duplicación innecesaria**: os documentos secundarios enlazan ao canónico en vez de repitílo.

## Índice por documento

| Documento | Cobre | Audiencia |
|-----------|-------|-----------|
| [FUNCIONAL.md](FUNCIONAL.md) | Valor real por papel e fluxos (festival, inscrición, comités, premios, xat/E2EE, votaxe do xurado) | usuario, admin, IA |
| [USO.md](USO.md) | Arranque, variables, migración SQLite↔MariaDB, copias, roles e operación | usuario, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoints `/api/admin`, conta inicial, rotación de secretos, límites, troubleshooting | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Perfís Docker, portos, vols, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, matriz `require_*`, perímetro, checklist de produción | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Mapa do sistema + regras backend/frontend + fluxos clave | dev, IA |
| [API.md](API.md) | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.md](DESARROLLO.md) | Convención para engadir endpoint/pantalla + portas CI | dev, IA |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Scripts `start.*`, builds distribuíbles, Docker, fixs CI | dev |
| [PUSH.md](PUSH.md) | Decisión de notificacións sen Firebase | dev |
| [DATABASE.md](DATABASE.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| [BACKEND.md](BACKEND.md) | Guía do backend (capas, config, auth, tests) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Informe de auditoría (rev. 10/10/2026) | referencia |
| [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md) | Protocolo de federación entre nodos (fase 4) | dev, IA |
| [FEDERATION_SCHEMA.md](FEDERATION_SCHEMA.md) | Clakettes Schema v1 (entidades mínimas federadas) | dev, IA |
| [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) | Modelo de confianza federado, mTLS, rotación de certificados | dev, IA |

## Ruta recomendada por perfil

### Usuario final

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) solo se precisan revisar permisos ou entorno de produción

### Administrador de despliegue

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
6. [BACKEND.md](BACKEND.md)

## Convencións para manter a documentación

- Actualiza o documento canónico antes que calquera resumo ou índice.
- Se mudas un fluxo de arranque, sincroniza [README.gl.md](../../README.gl.md), [USO.md](USO.md) e [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Se mudas unha API pública, actualiza [API.md](API.md) e, se procede, [DESARROLLO.md](DESARROLLO.md).
- Se mudas o esquema ou a persistencia, revisa [DATABASE.md](DATABASE.md) e as migracións.
- Sempre que edites un documento en `docs/es/`, replica o cambio ás 8 irmáns (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## FAQ rápida

- **Por onde comezo?** Lee [USO.md](USO.md) se vas operar a app; lee [ARQUITECTURA.md](ARQUITECTURA.md) se vas desenvolver.
- **Que é canónico e que non?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) e [DATABASE.md](DATABASE.md) son a referencia oficial para esos temas.
- **Onde atopo un comando ou script?** Revisa [HERRAMIENTAS.md](HERRAMIENTAS.md) e [../README.gl.md](../../README.gl.md).
- **Como sebo se un cambio require documentación?** Se afecta arranque, permisos, infraestrutura, API ou modelo de datos, debe reflectirse na documentación pertinente.

## Ver tamén

- [../README.gl.md](../../README.gl.md): visão xeral do proxecto
- [USO.md](USO.md): operación e configuración local
- [ADMINISTRACION.md](ADMINISTRACION.md): ámbito de despliegue e administración
- [ARQUITECTURA.md](ARQUITECTURA.md): mapa técnico do sistema
- [API.md](API.md): referencia de endpoints

## Inicio recomendado

Para comezar en entorno local:

```bash
cd backend && python -m uvicorn app.main:app --reload
cd frontend && flutter run
```

Ou, usando os scripts do proxecto:

```bat
start.bat --dev
```

A referencia completa de comandos e perfiles está en [HERRAMIENTAS.md](HERRAMIENTAS.md) e en [../README.gl.md](../../README.gl.md).