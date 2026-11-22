# Documentació — Clakettes

Aquest índex és l'entrada principal de la documentació del projecte. Està pensat perquè un usuari, un administrador o un desenvolupador trobi la guia correcta sense llegir fitxers a l'atzar.

## Idiomes

Els 18 documents comuns existeixen en les 9 llengües de la plataforma; a `docs/es/` hi ha a més dues anàlisis específiques (`AMENAZAS_NODOS_FEDERACION.md` i `MODELO_CONFIANZA_NODOS.md`). L'espanyol (canari) és el canònic:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

## Com navegar per la documentació

- **Vull utilitzar l'app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Administre un desplegament** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Desenvolupament** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md) + [BACKEND.md](BACKEND.md) + [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md)
- **Referència per a agents** → les ordres i convencions de desenvolupament estan a [../AGENTS.md](../../AGENTS.md)

## Principis de la documentació

- **Un sol document canònic per tema**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) i [API.md](API.md) són la referència oficial del seu àmbit.
- **Documentació per audiència**: cada guia està escrita per a un tipus de lector, no per a un sol conjunt d'ordres.
- **Enllaços directes**: des d'aquí es pot arribar al contingut rellevant en menys d'un clic.
- **Sense duplicació innecessària**: els documents secundaris enllacen al canònic en lloc de repetir-lo.

## Índex per document

| Document | Què cobreix | Audiència |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Utilitat real per rol i fluxos (festival, inscripció, comitès, premis, xat/E2EE, votació del jurat) | usuari, admin |
| [USO.md](USO.md) | Arrancada, variables, migració SQLite↔MariaDB, còpies de seguretat, rols i operació | usuari, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoints `/api/admin`, compte inicial, rotació de secrets, límits, resolució de problemes | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Perfils Docker, ports, volums, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, matriu `require_*`, perímetre, llista de comprovació de producció | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Mapa del sistema + regles backend/frontend + fluxos clau | dev |
| [API.md](API.md) | Referència d'endpoints | dev |
| [DESARROLLO.md](DESARROLLO.md) | Convenció per afegir endpoint/pantalla + portes CI | dev |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Scripts `start.*`, builds distribuïbles, Docker, correccions CI | dev |
| [PUSH.md](PUSH.md) | Decisió de notificacions sense Firebase | dev |
| [DATABASE.md](DATABASE.md) | Esquema dual SQLite/MariaDB, fitxes per model, ER | dev |
| [BACKEND.md](BACKEND.md) | Guia del backend (capes, configuració, auth, proves) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Informe d'auditoria (rev. 10/10/2026) | referència |
| [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md) | Protocol de federació entre nodes (fases 2 a 10) | dev |
| [FEDERATION_SCHEMA.md](FEDERATION_SCHEMA.md) | Clakettes Schema v1 (entitats mínimes federades) | dev |
| [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) | Model de confiança federat, mTLS, manifest signat, portabilitat, xat i resiliència | dev |
| [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md) | Decisió de broker (NATS JetStream) per al xat i els esdeveniments entre nodes; transport implementat avui: `DurableQueueBackend` sobre `chat_outbox` amb WebSocket de vora | dev |
| [AMENAZAS_NODOS_FEDERACION.md](../es/AMENAZAS_NODOS_FEDERACION.md) | Model d'amenaces de nodes federats (només en espanyol) | dev |
| [MODELO_CONFIANZA_NODOS.md](../es/MODELO_CONFIANZA_NODOS.md) | Model de confiança entre nodes (només en espanyol) | dev |

## Ruta recomanada per perfil

### Usuari final

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) només si cal revisar permisos o l'entorn de producció

### Administrador de desplegament

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Desenvolupador

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.md](API.md)
5. [DATABASE.md](DATABASE.md)
6. [BACKEND.md](BACKEND.md)
7. [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md)
8. [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md)
9. [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md)

## Convencions per mantenir la documentació

- Actualitza el document canònic abans que qualsevol resum o índex.
- Si canvies un flux d'arrancada, sincronitza [README.ca.md](../../README.ca.md), [USO.md](USO.md) i [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Si canvies una API pública, actualitza [API.md](API.md) i, si escau, [DESARROLLO.md](DESARROLLO.md).
- Si canvies l'esquema o la persistència, revisa [DATABASE.md](DATABASE.md) i les migracions.
- Cada cop que editis un document a `docs/es/`, replica el canvi a les 8 germanes (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## Preguntes freqüents ràpides

- **Per on començo?** Llegeix [USO.md](USO.md) si vas a operar l'app; llegeix [ARQUITECTURA.md](ARQUITECTURA.md) si vas a desenvolupar.
- **Què és canònic i què no?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) i [DATABASE.md](DATABASE.md) són la referència oficial per a aquests temes.
- **On trobo una ordre o script?** Revisa [HERRAMIENTAS.md](HERRAMIENTAS.md) i [../README.ca.md](../../README.ca.md).
- **Com sé si un canvi requereix documentació?** Si afecta l'arrancada, permisos, infraestructura, API o model de dades, ha de reflectir-se en la documentació pertinent.

## Vegeu també

- [../README.ca.md](../../README.ca.md): vista general del projecte
- [USO.md](USO.md): operació i configuració local
- [ADMINISTRACION.md](ADMINISTRACION.md): àmbit de desplegament i administració
- [ARQUITECTURA.md](ARQUITECTURA.md): mapa tècnic del sistema
- [API.md](API.md): referència d'endpoints
