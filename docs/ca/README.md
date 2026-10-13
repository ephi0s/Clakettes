# Documentació — Clakettes

Tota la documentació existeix en les 9 llengües de la plataforma. L'espanyol és canònic:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

Aquest índex és l'entrada principal de la documentació del projecte. Està pensat perquè un usuari, un administrador o un desenvolupador trobi la guia correcta sense llegir fitxers a l'atzar.

## Com navegar per la documentació

- **Vull utilitzar l'app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Administro un desplegament** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Desenvolupament** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](../es/API.md) + [DATABASE.md](DATABASE.md)
- **IA / agent** → [ARQUITECTURA.md](ARQUITECTURA.md) i el document de la tasca; les ordres i convencions obligatòries són a [../AGENTS.md](../../AGENTS.md)

## Principis de la documentació

- **Un sol document canònic per tema**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) i [API.md](../es/API.md) són la referència oficial del seu àmbit.
- **Documentació per audiència**: cada guia està escrita per a un tipus de lector, no per a un sol conjunt d'ordres.
- **Enllaços directes**: des d'aquí es pot arribar al contingut rellevant en menys d'un clic.
- **Sense duplicació innecessària**: els documents secundaris enllacen al canònic en lloc de repetir-lo.

## Índex per document

| Documento | Qué cubre | Audiencia |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Utilidad real por rol y flujos (festival, inscripción, comités, premios, chat/E2EE) | usuario, admin, IA |
| [USO.md](USO.md) | Arranque, variables, migración SQLite↔MariaDB, backups, roles y operación | usuario, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoints `/api/admin`, cuenta inicial, rotación de secretos, límites, troubleshooting | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Perfiles Docker, puertos, volúmenes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, matriz `require_*`, perímetro, checklist producción | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Mapa sistema + reglas backend/frontend + flujos clave | dev, IA |
| [API.md](../es/API.md) | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.md](DESARROLLO.md) | Convención para añadir endpoint/pantalla + puertas CI | dev, IA |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Scripts `start.*`, builds distribuibles, Docker, fixes CI | dev |
| [PUSH.md](PUSH.md) | Decisión de notificaciones sin Firebase | dev |
| [DATABASE.md](DATABASE.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| [BACKEND.md](BACKEND.md) | Guía del backend (capas, config, auth, tests) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Informe de auditoría (rev. 10/10/2026) | referencia |

## Ruta recomanada per perfil

### Usuari final

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) solo si necesitan revisar permisos o entorno productivo

### Administrador de desplegament

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Desenvolupador

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.md](../es/API.md)
5. [DATABASE.md](DATABASE.md)

## Convencions per mantenir la documentació

- Actualitza el document canònic abans que qualsevol resum o índex.
- Si canvies un flux d'arrencada, sincronitza [README.ca.md](../../README.ca.md), [USO.md](USO.md) i [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Si canvies una API pública, actualitza [API.md](../es/API.md) i, si escau, [DESARROLLO.md](DESARROLLO.md).
- Si canvies l'esquema o la persistència, revisa [DATABASE.md](DATABASE.md) i les migracions.

## FAQ ràpida

- **Per on començo?** Llegeix [USO.md](USO.md) si operaras l'app; llegeix [ARQUITECTURA.md](ARQUITECTURA.md) si desenvoluparàs.
- **Què és canònic i què no?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](../es/API.md) i [DATABASE.md](DATABASE.md) són la referència oficial per a aquests temes.
- **On trobo una ordre o script?** Revisa [HERRAMIENTAS.md](HERRAMIENTAS.md) i [../README.ca.md](../../README.ca.md).
- **Com sé si un canvi requereix documentació?** Si afecta arrencada, permisos, infraestructura, API, o model de dades, ha de reflectir-se en la documentació pertinent.

## Vegeu també

- [../README.ca.md](../../README.ca.md): vista general del projecte
- [USO.md](USO.md): operació i configuració local
- [ADMINISTRACION.md](ADMINISTRACION.md): àmbit de desplegament i administració
- [ARQUITECTURA.md](ARQUITECTURA.md): mapa tècnic del sistema
- [API.md](../es/API.md): referència d'endpoints

## Inici recomanat

Per començar en un entorn local:

```bash
cd backend && python -m uvicorn app.main:app --reload
cd frontend && flutter run
```

O, utilitzant els scripts del projecte:

```bat
start.bat --dev
```

La referència completa d'ordres i perfils del projecte és a [HERRAMIENTAS.md](HERRAMIENTAS.md) i a [../README.ca.md](../../README.ca.md).
