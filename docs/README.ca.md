# Documentació — Clakettes

Tota la documentació existeix en les 9 llengües de la plataforma. L'espanyol és canònic:
[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Aquest índex és l'entrada principal de la documentació del projecte. Està pensat perquè un usuari, un administrador o un desenvolupador trobi la guia correcta sense llegir fitxers a l'atzar.

## Com navegar per la documentació

- **Vull utilitzar l'app** → [USO.ca.md](USO.ca.md) + [FUNCIONAL.ca.md](FUNCIONAL.ca.md)
- **Administro un desplegament** → [ADMINISTRACION.ca.md](ADMINISTRACION.ca.md) + [INFRAESTRUCTURA.ca.md](INFRAESTRUCTURA.ca.md) + [SEGURIDAD.ca.md](SEGURIDAD.ca.md)
- **Desenvolupament** → [ARQUITECTURA.ca.md](ARQUITECTURA.ca.md) + [DESARROLLO.ca.md](DESARROLLO.ca.md) + [API.md](API.md) + [DATABASE.ca.md](DATABASE.ca.md)
- **IA / agent** → [ARQUITECTURA.ca.md](ARQUITECTURA.ca.md) i el document de la tasca; les ordres i convencions obligatòries són a [../AGENTS.md](../AGENTS.md)

## Principis de la documentació

- **Un sol document canònic per tema**: [SEGURIDAD.ca.md](SEGURIDAD.ca.md), [USO.ca.md](USO.ca.md), [DATABASE.ca.md](DATABASE.ca.md) i [API.md](API.md) són la referència oficial del seu àmbit.
- **Documentació per audiència**: cada guia està escrita per a un tipus de lector, no per a un sol conjunt d'ordres.
- **Enllaços directes**: des d'aquí es pot arribar al contingut rellevant en menys d'un clic.
- **Sense duplicació innecessària**: els documents secundaris enllacen al canònic en lloc de repetir-lo.

## Índex per document

| Documento | Qué cubre | Audiencia |
|---|---|---|
| [FUNCIONAL.ca.md](FUNCIONAL.ca.md) | Utilidad real por rol y flujos (festival, inscripción, comités, premios, chat/E2EE) | usuario, admin, IA |
| [USO.ca.md](USO.ca.md) | Arranque, variables, migración SQLite↔MariaDB, backups, roles y operación | usuario, admin |
| [ADMINISTRACION.ca.md](ADMINISTRACION.ca.md) | Endpoints `/api/admin`, cuenta inicial, rotación de secretos, límites, troubleshooting | admin |
| [INFRAESTRUCTURA.ca.md](INFRAESTRUCTURA.ca.md) | Perfiles Docker, puertos, volúmenes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.ca.md](SEGURIDAD.ca.md) | Tokens, matriz `require_*`, perímetro, checklist producción | admin, dev |
| [ARQUITECTURA.ca.md](ARQUITECTURA.ca.md) | Mapa sistema + reglas backend/frontend + flujos clave | dev, IA |
| [API.md](API.md) | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.ca.md](DESARROLLO.ca.md) | Convención para añadir endpoint/pantalla + puertas CI | dev, IA |
| [HERRAMIENTAS.ca.md](HERRAMIENTAS.ca.md) | Scripts `start.*`, builds distribuibles, Docker, fixes CI | dev |
| [PUSH.ca.md](PUSH.ca.md) | Decisión de notificaciones sin Firebase | dev |
| [DATABASE.ca.md](DATABASE.ca.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| [BACKEND.ca.md](BACKEND.ca.md) | Guía del backend (capas, config, auth, tests) | dev |
| [AUDITORIA.ca.md](AUDITORIA.ca.md) | Informe de auditoría (rev. 10/10/2026) | referencia |

## Ruta recomanada per perfil

### Usuari final

1. [USO.ca.md](USO.ca.md)
2. [FUNCIONAL.ca.md](FUNCIONAL.ca.md)
3. [SEGURIDAD.ca.md](SEGURIDAD.ca.md) solo si necesitan revisar permisos o entorno productivo

### Administrador de desplegament

1. [ADMINISTRACION.ca.md](ADMINISTRACION.ca.md)
2. [INFRAESTRUCTURA.ca.md](INFRAESTRUCTURA.ca.md)
3. [SEGURIDAD.ca.md](SEGURIDAD.ca.md)
4. [USO.ca.md](USO.ca.md)

### Desenvolupador

1. [../AGENTS.md](../AGENTS.md)
2. [ARQUITECTURA.ca.md](ARQUITECTURA.ca.md)
3. [DESARROLLO.ca.md](DESARROLLO.ca.md)
4. [API.md](API.md)
5. [DATABASE.ca.md](DATABASE.ca.md)

## Convencions per mantenir la documentació

- Actualitza el document canònic abans que qualsevol resum o índex.
- Si canvies un flux d'arrencada, sincronitza [README.ca.md](../README.ca.md), [USO.ca.md](USO.ca.md) i [HERRAMIENTAS.ca.md](HERRAMIENTAS.ca.md).
- Si canvies una API pública, actualitza [API.md](API.md) i, si escau, [DESARROLLO.ca.md](DESARROLLO.ca.md).
- Si canvies l'esquema o la persistència, revisa [DATABASE.ca.md](DATABASE.ca.md) i les migracions.

## FAQ ràpida

- **Per on començo?** Llegeix [USO.ca.md](USO.ca.md) si operaras l'app; llegeix [ARQUITECTURA.ca.md](ARQUITECTURA.ca.md) si desenvoluparàs.
- **Què és canònic i què no?** [USO.ca.md](USO.ca.md), [SEGURIDAD.ca.md](SEGURIDAD.ca.md), [API.md](API.md) i [DATABASE.ca.md](DATABASE.ca.md) són la referència oficial per a aquests temes.
- **On trobo una ordre o script?** Revisa [HERRAMIENTAS.ca.md](HERRAMIENTAS.ca.md) i [../README.ca.md](../README.ca.md).
- **Com sé si un canvi requereix documentació?** Si afecta arrencada, permisos, infraestructura, API, o model de dades, ha de reflectir-se en la documentació pertinent.

## Vegeu també

- [../README.ca.md](../README.ca.md): vista general del projecte
- [USO.ca.md](USO.ca.md): operació i configuració local
- [ADMINISTRACION.ca.md](ADMINISTRACION.ca.md): àmbit de desplegament i administració
- [ARQUITECTURA.ca.md](ARQUITECTURA.ca.md): mapa tècnic del sistema
- [API.md](API.md): referència d'endpoints

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

La referència completa d'ordres i perfils del projecte és a [HERRAMIENTAS.ca.md](HERRAMIENTAS.ca.md) i a [../README.ca.md](../README.ca.md).
