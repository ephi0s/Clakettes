# Documentacion — Clakettes

Tota la documentacion existís dins las 9 lengas de la plataforma. L'espanhòl es canonic:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](README.md)

Aqueste indici es l'intrada principala de la documentacion del projècte. Es pensat per qu'un utilizaire, un administrator o un desvolopaire trobe la guida corrècta sens legir fichièrs a l'azard.

## Cossí navegar per la documentacion

- **Vòli utilizar l'app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Administri un desplegament** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Desvolopament** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.oc.md](API.md) + [DATABASE.md](DATABASE.md)
- **IA / agent** → [ARQUITECTURA.md](ARQUITECTURA.md) e lo document de la prètzfach; las comandas e convencions obligatòrias son en [../AGENTS.md](../../AGENTS.md)

## Principis de la documentacion

- **Un sol document canonic per tèma**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) e [API.oc.md](API.md) son la referéncia oficiala de son domeni.
- **Documentacion per audiéncia**: cada guida es escricha per un tipe de legeire, non per un sol ensems de comandas.
- **Ligams dirèctes**: dempuèi aicí se pòt arribar al contengut pertinent en mens d'un clic.
- **Sens duplicacion inutila**: los documents secondaris ligan cap al canonic en luòc de repetir.

## Indici per document

| Documento | Qué cubre | Audiencia |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Utilidad real por rol y flujos (festival, inscripción, comités, premios, chat/E2EE) | usuario, admin, IA |
| [USO.md](USO.md) | Arranque, variables, migración SQLite↔MariaDB, backups, roles y operación | usuario, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoints `/api/admin`, cuenta inicial, rotación de secretos, límites, troubleshooting | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Perfiles Docker, puertos, volúmenes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, matriz `require_*`, perímetro, checklist producción | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Mapa sistema + reglas backend/frontend + flujos clave | dev, IA |
| [API.oc.md](API.md) | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.md](DESARROLLO.md) | Convención para añadir endpoint/pantalla + puertas CI | dev, IA |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Scripts `start.*`, builds distribuibles, Docker, fixes CI | dev |
| [PUSH.md](PUSH.md) | Decisión de notificaciones sin Firebase | dev |
| [DATABASE.md](DATABASE.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| [BACKEND.md](BACKEND.md) | Guía del backend (capas, config, auth, tests) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Informe de auditoría (rev. 10/10/2026) | referencia |

## Ruta recomandada per perfil

### Utilizaire finau

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) sonque se an besonh de revisar permissions o environa productiva

### Administrator de desplegament

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Desvolopaire

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.oc.md](API.md)
5. [DATABASE.md](DATABASE.md)

## Convencions per manténer la documentacion

- Actualiza lo document canonic abans que qual que siá resumit o indici.
- Se cambias un flux d'aviada, sincroniza [README.oc.md](../../README.oc.md), [USO.md](USO.md) e [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Se cambias una API publica, actualiza [API.oc.md](API.md) e, s'escaire, [DESARROLLO.md](DESARROLLO.md).
- Se cambias l'esquèma o la persisténcia, revisa [DATABASE.md](DATABASE.md) e las migracions.

## FAQ rapida

- **Per ont comenci?** Legís [USO.md](USO.md) se vas operar l'app; legís [ARQUITECTURA.md](ARQUITECTURA.md) se vas desvolopar.
- **Qu'es canonic e qu'es pas?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.oc.md](API.md) e [DATABASE.md](DATABASE.md) son la referéncia oficiala per aquelses tèmas.
- **Ont trobi una comanda o script?** Revisa [HERRAMIENTAS.md](HERRAMIENTAS.md) e [../README.oc.md](../../README.oc.md).
- **Cossí sai se un cambi requerís documentacion?** S'afècta aviada, permissions, infraestructura, API, o modèl de donadas, deu se rebatre dins la documentacion pertinenta.

## Veire tanben

- [../README.oc.md](../../README.oc.md): vista generala del projècte
- [USO.md](USO.md): operacion e configuracion locala
- [ADMINISTRACION.md](ADMINISTRACION.md): domeni de desplegament e administracion
- [ARQUITECTURA.md](ARQUITECTURA.md): mapa tecnica del sistèma
- [API.oc.md](API.md): referéncia d'endpoints

## Aviada recomandada

Per començar en un environa locau:

```bash
cd backend && python -m uvicorn app.main:app --reload
cd frontend && flutter run
```

O, en utilizant los scripts del projècte:

```bat
start.bat --dev
```

La referéncia completa de comandas e perfils del projècte es en [HERRAMIENTAS.md](HERRAMIENTAS.md) e en [../README.oc.md](../../README.oc.md).
