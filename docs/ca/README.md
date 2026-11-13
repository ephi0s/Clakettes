# Documentació — Clakettes

Aquest índex és l'entrada principal de la documentació del projecte. Está pensat perquè un usuari, un administrador o un desenvolupador trobi la guia correcta sense llegir fitxers a l'atzar.

## Idiomes

Tota la documentació existeix en les 9 llengües de la plataforma. L'espanyol (canónic) és l'idioma base:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

## Com navegar per la documentació

- **Vull utilitzar l'aplicació** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Administre un desplegament** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Desenvolupament** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md) + [BACKEND.md](BACKEND.md)
- **IA / agent** → [ARQUITECTURA.md](ARQUITECTURA.md) i el document de la tasca; les ordres i convencions obligatòries estan a [../AGENTS.md](../../AGENTS.md)

## Principis de la documentació

- **Un sol document canònic per tema**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) i [API.md](API.md) són la referència oficial del seu àmbit.
- **Documentació per audiència**: cada guia està escrita per a un tipus de lector, no per a un sol conjunt d'ordres.
- **Enllaços directes**: des d'aquí es pot arribar al contingut rellevant en menys d'un clic.
- **Sense duplicació innecessària**: els documents secundaris enllacen al canònic en lloc de repetir-lo.

## Índex per document

| Document | Què cobreix | Audiència |
|----------|-------------|-----------|
| [FUNCIONAL.md](FUNCIONAL.md) | Valor real per rol i fluxos (festival, inscripció, comitats, premis, xat/E2EE, vot jurat) | usuari, admin, IA |
| [USO.md](USO.md) | Arrancada, variables, migració SQLite↔MariaDB, còpies de seguretat, funcions, operació | usuari, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoints `/api/admin`, compte inicial, rotació de secrets, límits, solució de problemes | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Perfils Docker, ports, volumens, Nginx, salud, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, matriu `require_*`, perímetre, llista de comprovació de producció | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Mapa del sistema + regles backend/frontend + fluxos clau | dev, IA |
| [API.md](API.md) | Referència d'endpoints (regenerable amb `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.md](DESARROLLO.md) | Conveció per afegir endpoint/pantalla + portes CI | dev, IA |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Scripts `start.*`, builds distribuïbles, Docker, correccions CI | dev |
| [PUSH.md](PUSH.md) | Decisió de notificacions sense Firebase | dev |
| [DATABASE.md](DATABASE.md) | Esquema dual SQLite/MariaDB, fitxes per model, ER | dev, IA |
| [BACKEND.md](BACKEND.md) | Guia del backend (capes, configuració, autenticació, proves) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Informe d'auditoria (rev. 10/10/2026) | referència |
| [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md) | Protocolo de federació entre nodes (fase 4) | dev, IA |
| [FEDERATION_SCHEMA.md](FEDERATION_SCHEMA.md) | Clakettes Schema v1 (entitats mínimes federades) | dev, IA |
| [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) | Model de confiança federat, mTLS, rotació de certificats | dev, IA |

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

## Convecions per mantenir la documentació

- Actualitza el document canònic abans que qualsevol resum o índex.
- Si canvies un flux d'arrancada, sincronitza [README.ca.md](../../README.ca.md), [USO.md](USO.md) i [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Si canvies una API pública, actualitza [API.md](API.md) i, si escau, [DESARROLLO.md](DESARROLLO.md).
- Si canvies l'esquema o la persistència, revisa [DATABASE.md](DATABASE.md) i les migracions.
- Cada cop que editis un document a `docs/es/`, replica el canvi a les 8 germanes (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## FAQ ràpida

- **Per on comencem?** Llegiu [USO.md](USO.md) si exploitareu l'aplicació; llegiu [ARQUITECTURA.md](ARQUITECTURA.md) si desenvolupareu.
- **Què és canònic i què no?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) i [DATABASE.md](DATABASE.md) són la referència oficial per a aquests temes.
- **On trobo una ordre o script?** Revisa [HERRAMIENTAS.md](HERRAMIENTAS.md) i [../README.ca.md](../../README.ca.md).
- **Com sé si un canvi requereix documentació?** Si afecta l'arrancada, permisos, infraestructura, API o model de dades, ha de reflectir-se en la documentació pertinent.

## Vegeu també

- [../README.ca.md](../../README.ca.md): vista general del projecte
- [USO.md](USO.md): operació i configuració local
- [ADMINISTRACION.md](ADMINISTRACION.md): àmbit de desplegament i administració
- [ARQUITECTURA.md](ARQUITECTURA.md): mapa tècnic del sistema
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

La referència completa d'ordres i perfils del projecte està a [HERRAMIENTAS.md](HERRAMIENTAS.md) i a [../README.ca.md](../../README.ca.md).