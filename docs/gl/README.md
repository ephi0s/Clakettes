# Documentación — Clakettes

Este índice é a entrada principal da documentación do proxecto. Está pensado para que un usuario, un administrador ou un desenvolvedor atope a guía correcta sen ler arquivos ao azar.

## Idiomas

Os documentos comúns existen en todas as linguas da plataforma; en `docs/es/` hai ademais dous análisis específicos (`AMENAZAS_NODOS_FEDERACION.md` e `MODELO_CONFIANZA_NODOS.md`). O español (canario) é o canónico:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](README.md) · [OC](../oc/README.md)

## Como navegar pola documentación

- **Quero usar a app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Administro un despregue** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Desenvolvemento** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md) + [BACKEND.md](BACKEND.md) + [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md)
- **Referencia para axentes** → os comandos e convencións de desenvolvemento están en [../AGENTS.md](../../AGENTS.md)

## Principios da documentación

- **Un único documento canónico por tema**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) e [API.md](API.md) son a referencia oficial do seu ámbito.
- **Documentación por audiencia**: cada guía está escrita para un tipo de lector, non para un único conxunto de comandos.
- **Ligazóns directas**: desde aquí pódese chegar ao contido relevante en menos dun clic.
- **Sen duplicación innecesaria**: os documentos secundarios ligan ao canónico en lugar de repetilo.

## Índice por documento

| Documento | Que cobre | Audiencia |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Utilidade real por rol e fluxos (festival, inscrición, comités, premios, chat/E2EE, votación do xurado) | usuario, admin |
| [USO.md](USO.md) | Arranque, variables, migración SQLite↔MariaDB, copias de seguridade, roles e operación | usuario, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoints `/api/admin`, conta inicial, rotación de segredos, límites, resolución de problemas | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Perfis Docker, portos, volumes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, matriz `require_*`, perímetro, checklist de produción | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Mapa do sistema + regras backend/frontend + fluxos clave | dev |
| [API.md](API.md) | Referencia de endpoints | dev |
| [DESARROLLO.md](DESARROLLO.md) | Convención para engadir endpoint/pantalla + portas CI | dev |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Scripts `start.*`, builds distribuíbles, Docker, correccións CI | dev |
| [PUSH.md](PUSH.md) | Decisión de notificacións sen Firebase | dev |
| [DATABASE.md](DATABASE.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev |
| [BACKEND.md](BACKEND.md) | Guía do backend (capas, configuración, auth, tests) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Informe de auditoría (rev. 10/10/2026) | referencia |
| [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md) | Protocolo de federación entre nodos (fases 2 a 10) | dev |
| [FEDERATION_SCHEMA.md](FEDERATION_SCHEMA.md) | Clakettes Schema v1 (entidades mínimas federadas) | dev |
| [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) | Modelo de confianza federado, mTLS, manifesto asinado, portabilidade, chat e resiliencia | dev |
| [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md) | Decisión de broker (NATS JetStream) para o chat e os eventos entre nodos; transporte implementado hoxe: `DurableQueueBackend` sobre `chat_outbox` con WebSocket de borde | dev |
| [AMENAZAS_NODOS_FEDERACION.md](../es/AMENAZAS_NODOS_FEDERACION.md) | Modelo de ameazas de nodos federados (só en español) | dev |
| [MODELO_CONFIANZA_NODOS.md](../es/MODELO_CONFIANZA_NODOS.md) | Modelo de confianza entre nodos (só en español) | dev |

## Ruta recomendada por perfil

### Usuario final

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) só se precisan revisar permisos ou o contorno de produción

### Administrador de despregue

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
7. [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md)
8. [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md)
9. [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md)

## Convencións para manter a documentación

- Actualiza o documento canónico antes que calquera resumo ou índice.
- Se cambias un fluxo de arranque, sincroniza [README.gl.md](../../README.gl.md), [USO.md](USO.md) e [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Se cambias unha API pública, actualiza [API.md](API.md) e, se procede, [DESARROLLO.md](DESARROLLO.md).
- Se cambias o esquema ou a persistencia, revisa [DATABASE.md](DATABASE.md) e as migracións.
- Sempre que edites un documento en `docs/es/`, replica o cambio en todos os documentos irmáns (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## FAQ rápida

- **Por onde comezo?** Le [USO.md](USO.md) se vas operar a app; le [ARQUITECTURA.md](ARQUITECTURA.md) se vas desenvolver.
- **Que é canónico e que non?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) e [DATABASE.md](DATABASE.md) son a referencia oficial para eses temas.
- **Onde atopo un comando ou script?** Revisa [HERRAMIENTAS.md](HERRAMIENTAS.md) e [../README.gl.md](../../README.gl.md).
- **Como sei se un cambio require documentación?** Se afecta ao arranque, permisos, infraestrutura, API ou modelo de datos, debe reflectirse na documentación pertinente.

## Ver tamén

- [../README.gl.md](../../README.gl.md): visión xeral do proxecto
- [USO.md](USO.md): operación e configuración local
- [ADMINISTRACION.md](ADMINISTRACION.md): ámbito de despregue e administración
- [ARQUITECTURA.md](ARQUITECTURA.md): mapa técnico do sistema
- [API.md](API.md): referencia de endpoints
