# Documentacion — Clakettes

Tota la documentacion existís dins las 9 lengas de la plataforma. L'espanhòl es canonic:
[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Aqueste indici es l'intrada principala de la documentacion del projècte. Es pensat per qu'un utilizaire, un administrator o un desvolopaire trobe la guida corrècta sens legir fichièrs a l'azard.

## Cossí navegar per la documentacion

- **Vòli utilizar l'app** → [USO.oc.md](USO.oc.md) + [FUNCIONAL.oc.md](FUNCIONAL.oc.md)
- **Administri un desplegament** → [ADMINISTRACION.oc.md](ADMINISTRACION.oc.md) + [INFRAESTRUCTURA.oc.md](INFRAESTRUCTURA.oc.md) + [SEGURIDAD.oc.md](SEGURIDAD.oc.md)
- **Desvolopament** → [ARQUITECTURA.oc.md](ARQUITECTURA.oc.md) + [DESARROLLO.oc.md](DESARROLLO.oc.md) + [API.oc.md](API.oc.md) + [DATABASE.oc.md](DATABASE.oc.md)
- **IA / agent** → [ARQUITECTURA.oc.md](ARQUITECTURA.oc.md) e lo document de la prètzfach; las comandas e convencions obligatòrias son en [../AGENTS.md](../AGENTS.md)

## Principis de la documentacion

- **Un sol document canonic per tèma**: [SEGURIDAD.oc.md](SEGURIDAD.oc.md), [USO.oc.md](USO.oc.md), [DATABASE.oc.md](DATABASE.oc.md) e [API.oc.md](API.oc.md) son la referéncia oficiala de son domeni.
- **Documentacion per audiéncia**: cada guida es escricha per un tipe de legeire, non per un sol ensems de comandas.
- **Ligams dirèctes**: dempuèi aicí se pòt arribar al contengut pertinent en mens d'un clic.
- **Sens duplicacion inutila**: los documents secondaris ligan cap al canonic en luòc de repetir.

## Indici per document

| Documento | Qué cubre | Audiencia |
|---|---|---|
| [FUNCIONAL.oc.md](FUNCIONAL.oc.md) | Utilidad real por rol y flujos (festival, inscripción, comités, premios, chat/E2EE) | usuario, admin, IA |
| [USO.oc.md](USO.oc.md) | Arranque, variables, migración SQLite↔MariaDB, backups, roles y operación | usuario, admin |
| [ADMINISTRACION.oc.md](ADMINISTRACION.oc.md) | Endpoints `/api/admin`, cuenta inicial, rotación de secretos, límites, troubleshooting | admin |
| [INFRAESTRUCTURA.oc.md](INFRAESTRUCTURA.oc.md) | Perfiles Docker, puertos, volúmenes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.oc.md](SEGURIDAD.oc.md) | Tokens, matriz `require_*`, perímetro, checklist producción | admin, dev |
| [ARQUITECTURA.oc.md](ARQUITECTURA.oc.md) | Mapa sistema + reglas backend/frontend + flujos clave | dev, IA |
| [API.oc.md](API.oc.md) | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.oc.md](DESARROLLO.oc.md) | Convención para añadir endpoint/pantalla + puertas CI | dev, IA |
| [HERRAMIENTAS.oc.md](HERRAMIENTAS.oc.md) | Scripts `start.*`, builds distribuibles, Docker, fixes CI | dev |
| [PUSH.oc.md](PUSH.oc.md) | Decisión de notificaciones sin Firebase | dev |
| [DATABASE.oc.md](DATABASE.oc.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| [BACKEND.oc.md](BACKEND.oc.md) | Guía del backend (capas, config, auth, tests) | dev |
| [AUDITORIA.oc.md](AUDITORIA.oc.md) | Informe de auditoría (rev. 10/10/2026) | referencia |

## Ruta recomandada per perfil

### Utilizaire finau

1. [USO.oc.md](USO.oc.md)
2. [FUNCIONAL.oc.md](FUNCIONAL.oc.md)
3. [SEGURIDAD.oc.md](SEGURIDAD.oc.md) sonque se an besonh de revisar permissions o environa productiva

### Administrator de desplegament

1. [ADMINISTRACION.oc.md](ADMINISTRACION.oc.md)
2. [INFRAESTRUCTURA.oc.md](INFRAESTRUCTURA.oc.md)
3. [SEGURIDAD.oc.md](SEGURIDAD.oc.md)
4. [USO.oc.md](USO.oc.md)

### Desvolopaire

1. [../AGENTS.md](../AGENTS.md)
2. [ARQUITECTURA.oc.md](ARQUITECTURA.oc.md)
3. [DESARROLLO.oc.md](DESARROLLO.oc.md)
4. [API.oc.md](API.oc.md)
5. [DATABASE.oc.md](DATABASE.oc.md)

## Convencions per manténer la documentacion

- Actualiza lo document canonic abans que qual que siá resumit o indici.
- Se cambias un flux d'aviada, sincroniza [README.oc.md](../README.oc.md), [USO.oc.md](USO.oc.md) e [HERRAMIENTAS.oc.md](HERRAMIENTAS.oc.md).
- Se cambias una API publica, actualiza [API.oc.md](API.oc.md) e, s'escaire, [DESARROLLO.oc.md](DESARROLLO.oc.md).
- Se cambias l'esquèma o la persisténcia, revisa [DATABASE.oc.md](DATABASE.oc.md) e las migracions.

## FAQ rapida

- **Per ont comenci?** Legís [USO.oc.md](USO.oc.md) se vas operar l'app; legís [ARQUITECTURA.oc.md](ARQUITECTURA.oc.md) se vas desvolopar.
- **Qu'es canonic e qu'es pas?** [USO.oc.md](USO.oc.md), [SEGURIDAD.oc.md](SEGURIDAD.oc.md), [API.oc.md](API.oc.md) e [DATABASE.oc.md](DATABASE.oc.md) son la referéncia oficiala per aquelses tèmas.
- **Ont trobi una comanda o script?** Revisa [HERRAMIENTAS.oc.md](HERRAMIENTAS.oc.md) e [../README.oc.md](../README.oc.md).
- **Cossí sai se un cambi requerís documentacion?** S'afècta aviada, permissions, infraestructura, API, o modèl de donadas, deu se rebatre dins la documentacion pertinenta.

## Veire tanben

- [../README.oc.md](../README.oc.md): vista generala del projècte
- [USO.oc.md](USO.oc.md): operacion e configuracion locala
- [ADMINISTRACION.oc.md](ADMINISTRACION.oc.md): domeni de desplegament e administracion
- [ARQUITECTURA.oc.md](ARQUITECTURA.oc.md): mapa tecnica del sistèma
- [API.oc.md](API.oc.md): referéncia d'endpoints

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

La referéncia completa de comandas e perfils del projècte es en [HERRAMIENTAS.oc.md](HERRAMIENTAS.oc.md) e en [../README.oc.md](../README.oc.md).
