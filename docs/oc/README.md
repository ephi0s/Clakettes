# Documentacion — Clakettes

Aqueste index es l'entrada prenchipala de la documentacion del projècte. Es pensat per que un usagi, un administrador o un desenvolverdorr trova la guia correcha sens llegir fitxiers al azar.

## Lengas

Tota la documentacion existe nei 9 lengas de la plataforma. L'espaiòl (canario) es canonico:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](README.md)

## Navegar la documentacion

- **Voglì utiar l'app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Administro un desplegament** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Desenvolviment** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md) + [BACKEND.md](BACKEND.md)
- **IA / agent** → [ARQUITECTURA.md](ARQUITECTURA.md) e lo document de la tasca; las comandas e convencons obligatòrias son en [../AGENTS.md](../../AGENTS.md)

## Principis de la documentacion

- **Un sol document canonico per tema**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) e [API.md](API.md) son la referenzia oficial per lo so ambit.
- **Documentacion per audiencia**: cada guia es escrìta per un type de lectore, non per un sol conjon de comandas.
- **Enlaces directes**: desde aquì se pot arribar al contén pertinent en men d'un clic.
- **Sensa duplicacion innecesaria**: los documents secundaris enlacen al canonico en vez de repitir-lo.

## Index per document

| Documento | Que cover | Audiencia |
|-----------|-----------|-----------|
| [FUNCIONAL.md](FUNCIONAL.md) | Valor real per rol e fluxos (festival, inscripcion, comitots, premis, chate/E2EE, votaciu del jurat) | usagi, admin, IA |
| [USO.md](USO.md) | Arrancada, variables, migracion SQLite↔MariaDB, backup, ròls e operacion | usagi, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoints `/api/admin`, compte initial, rotacion de secrets, limites, solucion de problemas | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Perfils Docker, ports, volumens, Nginx, sanitat, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, matriza `require_*`, perimetre, checklist de produccion | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Mapa del sistema + regras backend/frontend + fluxos claus | dev, IA |
| [API.md](API.md) | Referenca d'endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.md](DESARROLLO.md) | Convencon per afegir endpoint/pantalla + portas CI | dev, IA |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Scripts `start.*`, builds distribuibles, Docker, fiças CI | dev |
| [PUSH.md](PUSH.md) | Decisio de notificacions sens Firebase | dev |
| [DATABASE.md](DATABASE.md) | Esquema dual SQLite/MariaDB, fichas per model, ER | dev, IA |
| [BACKEND.md](BACKEND.md) | Guia del backend (capas, config, auth, tests) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Raport d'auditoria (rev. 10/10/2026) | referenzia |
| [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md) | Protocolo de federacion entre nods (fasa 4) | dev, IA |
| [FEDERATION_SCHEMA.md](FEDERATION_SCHEMA.md) | Clakettes Schema v1 (entitats minimas federades) | dev, IA |
| [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) | Model de confianza federat, mTLS, rotacion de certificats | dev, IA |

## Ruta recomendada per profil

### Usagi final

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) solo si avèi necesià de revisar los permisos o l'entorn de produccion

### Administrador de desplegament

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Desenvolverdorr

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.md](API.md)
5. [DATABASE.md](DATABASE.md)
6. [BACKEND.md](BACKEND.md)

## Convencons per maintenir la documentacion

- Actualiza lo document canonico abans de cualquier resum o index.
- Si mudatz un flux d'arrancada, sincronizatz [README.oc.md](../../README.oc.md), [USO.md](USO.md) e [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Si mudatz una API publica, actualizatz [API.md](API.md) e, se cal, [DESARROLLO.md](DESARROLLO.md).
- Si mudatz l'esquema o la persistencia, revisatz [DATABASE.md](DATABASE.md) e las migracions.
- Cada cotz que editez un document en `docs/es/`, replicatz lo canvi a las 8 germanas (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## FAQ rapide

- **On comensatz?** Lengatz [USO.md](USO.md) si operatz l'app; lengatz [ARQUITECTURA.md](ARQUITECTURA.md) si developatz.
- **Qu'es canonico e qu'es pas?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) e [DATABASE.md](DATABASE.md) son la referenzia oficial per a esos temas.
- **On troba una comanda o un script?** Revisatz [HERRAMIENTAS.md](HERRAMIENTAS.md) e [../README.oc.md](../../README.oc.md).
- **Com sabetz se un canvi requeri documentacion?** Se afecte l'arrancada, los permisos, l'infraestrutura, l'API o lo model de donats, deu reflectirse en la documentacion pertinenta.

## Veire ancaus

- [../README.oc.md](../../README.oc.md): vista general del projècte
- [USO.md](USO.md): operacion e configuracion locala
- [ADMINISTRACION.md](ADMINISTRACION.md): ambit de desplegament e administratzia
- [ARQUITECTURA.md](ARQUITECTURA.md): mapa tecnico del sistema
- [API.md](API.md): referenca d'endpoints

## Inici recomendat

Per comensar en entorn local:

```bash
cd backend && python -m uvicorn app.main:app --reload
cd frontend && flutter run
```

O, usanz los scripts del projècte:

```bat
start.bat --dev
```

La referenca completa de comandas e perfilhs esta en [HERRAMIENTAS.md](HERRAMIENTAS.md) e en [../README.oc.md](../../README.oc.md).