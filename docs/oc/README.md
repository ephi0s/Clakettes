# Documentacion — Clakettes

Aqueste index es l'entrada principala de la documentacion del projècte. Es pensat per que un usagi, un administrador o un desenvolopador trobe la guia correcha sens legir de fitxiers a l'atzar.

## Lengas

Los documents comuns existisson dins totas las lengas de la plataforma; dins `docs/es/` i a en mai dos analisis especifics (`AMENAZAS_NODOS_FEDERACION.md` e `MODELO_CONFIANZA_NODOS.md`). L'espanhòl (canari) es lo canonic:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](README.md)

## Còm navegar la documentacion

- **Voli utilizar l'app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Administre un desplegament** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Desvolopament** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md) + [BACKEND.md](BACKEND.md) + [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md)
- **Referéncia pels agents** → las comandas e las convencions de desvolopament son dins [../AGENTS.md](../../AGENTS.md)

## Principis de la documentacion

- **Un sol document canonic per tèma**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) e [API.md](API.md) son la referéncia oficiala de lor domeni.
- **Documentacion per public**: cada guia es escricha per un tipe de lector, non per un sol ensemble de comandas.
- **Ligams directes**: d'aquí se pòt arribar al contengut util en mens d'un clic.
- **Pas de duplicacion inutila**: los documents segondaris ligan al canonic en luòc de lo repetir.

## Index per document

| Document | Quel cobrís | Public |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Utilitat reala per ròtle e fluxes (festival, inscripcion, comitats, prèmis, chat/E2EE, vot del jurat) | usagi, admin |
| [USO.md](USO.md) | Arranjada, variablas, migracion SQLite↔MariaDB, còpias de seguretat, ròtles e operacion | usagi, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoints `/api/admin`, compte inicial, rotacion dels secrets, limites, resolucion de problèmas | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Perfils Docker, pòrts, volums, Nginx, santat, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, matritz `require_*`, perimetre, lista de contraròtle de produccion | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Mapa del sistèma + reglas backend/frontend + fluxes claus | dev |
| [API.md](API.md) | Referéncia dels endpoints | dev |
| [DESARROLLO.md](DESARROLLO.md) | Convencion per ajustar un endpoint/ecran + pòrtas CI | dev |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Scripts `start.*`, builds distribuibles, Docker, correccions CI | dev |
| [PUSH.md](PUSH.md) | Decision de notificacions sens Firebase | dev |
| [DATABASE.md](DATABASE.md) | Esquèma dual SQLite/MariaDB, fichas per modèl, ER | dev |
| [BACKEND.md](BACKEND.md) | Guia del backend (cachas, configuracion, autentificacion, tèsts) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Rapòrt d'audit (rev. 10/10/2026) | referéncia |
| [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md) | Protocòl de federacion entre noses (fases 2 a 10) | dev |
| [FEDERATION_SCHEMA.md](FEDERATION_SCHEMA.md) | Clakettes Schema v1 (entitats minimalas federadas) | dev |
| [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) | Modèl de fisança federada, mTLS, manifest signat, portabilitat, chat e resiliéncia | dev |
| [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md) | Decision de broker (NATS JetStream) pel chat e los eveniments entre noses; transpòrt implementat avui: `DurableQueueBackend` sus `chat_outbox` amb WebSocket de riba | dev |
| [AMENAZAS_NODOS_FEDERACION.md](../es/AMENAZAS_NODOS_FEDERACION.md) | Model de menaças dels nodes federats (solament en espanhòl) | dev |
| [MODELO_CONFIANZA_NODOS.md](../es/MODELO_CONFIANZA_NODOS.md) | Modèl de fisança entre nodes (solament en espanhòl) | dev |

## Rota recomandada per profil

### Usagi final

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) solament se cal revisar las permission o l'environament de produccion

### Administrator de desplegament

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Desenvolopador

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.md](API.md)
5. [DATABASE.md](DATABASE.md)
6. [BACKEND.md](BACKEND.md)
7. [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md)
8. [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md)
9. [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md)

## Convencions per manténer la documentacion

- Actualizar lo document canonic abans que tot resumit o index.
- Se càmbias un flux d'arranjada, sincronizar [README.oc.md](../../README.oc.md), [USO.md](USO.md) e [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Se càmbias una API publica, actualizar [API.md](API.md) e, se cal, [DESARROLLO.md](DESARROLLO.md).
- Se càmbias l'esquèma o la persisténcia, revisar [DATABASE.md](DATABASE.md) e las migracions.
- Cada còp que editas un document dins `docs/es/`, replicar lo càmbio a totes las sòrs (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## FAQ rapida

- **Per ont comenci?** Legir [USO.md](USO.md) se vas operar l'app; legir [ARQUITECTURA.md](ARQUITECTURA.md) se vas desvolopar.
- **Qu es canonic e qu non?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) e [DATABASE.md](DATABASE.md) son la referéncia oficiala per aquestes tèmas.
- **Ont trobi una comanda o un script?** Revisar [HERRAMIENTAS.md](HERRAMIENTAS.md) e [../README.oc.md](../../README.oc.md).
- **Còm saber se un càmbio demanda documentacion?** Se tòca l'arranjada, las permission, l'infraestructura, l'API o lo modèl de donadas, deu èsser reflectit dins la documentacion pertinenta.

## Vejatz tanben

- [../README.oc.md](../../README.oc.md): vista generala del projècte
- [USO.md](USO.md): operacion e configuracion locala
- [ADMINISTRACION.md](ADMINISTRACION.md): domeni de desplegament e administracion
- [ARQUITECTURA.md](ARQUITECTURA.md): mapa tecnic del sistèma
- [API.md](API.md): referéncia dels endpoints
