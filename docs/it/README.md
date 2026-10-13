# Documentazione — Clakettes

Tutta la documentazione esiste nelle 9 lingue della piattaforma. Lo spagnolo è canonico:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

Questo indice è l'ingresso principale della documentazione del progetto. È pensato perché un utente, un amministratore o uno sviluppatore trovi la guida giusta senza leggere file a caso.

## Come navigare nella documentazione

- **Voglio usare l'app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Amministro un deployment** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Sviluppo** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](../es/API.md) + [DATABASE.md](DATABASE.md)
- **IA / agente** → [ARQUITECTURA.md](ARQUITECTURA.md) e il documento del compito; i comandi e le convenzioni obbligatorie sono in [../AGENTS.md](../../AGENTS.md)

## Principi della documentazione

- **Un solo documento canonico per tema**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) e [API.md](../es/API.md) sono il riferimento ufficiale del loro ambito.
- **Documentazione per pubblico**: ogni guida è scritta per un tipo di lettore, non per un solo insieme di comandi.
- **Link diretti**: da qui si può arrivare al contenuto rilevante in meno di un clic.
- **Senza duplicazione inutile**: i documenti secondari linkano il canonico invece di ripeterlo.

## Indice per documento

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

## Percorso consigliato per profilo

### Utente finale

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) solo se devono rivedere permessi o ambiente produttivo

### Amministratore del deployment

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Sviluppatore

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.md](../es/API.md)
5. [DATABASE.md](DATABASE.md)

## Convenzioni per mantenere la documentazione

- Aggiorna il documento canonico prima di qualunque riepilogo o indice.
- Se cambi un flusso di avvio, sincronizza [README.it.md](../../README.it.md), [USO.md](USO.md) e [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Se cambi un'API pubblica, aggiorna [API.md](../es/API.md) e, se del caso, [DESARROLLO.md](DESARROLLO.md).
- Se cambi lo schema o la persistenza, rivedi [DATABASE.md](DATABASE.md) e le migrazioni.

## FAQ rapida

- **Da dove comincio?** Leggi [USO.md](USO.md) se gestirai l'app; leggi [ARQUITECTURA.md](ARQUITECTURA.md) se svilupperai.
- **Cosa è canonico e cosa no?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](../es/API.md) e [DATABASE.md](DATABASE.md) sono il riferimento ufficiale per quei temi.
- **Dove trovo un comando o script?** Controlla [HERRAMIENTAS.md](HERRAMIENTAS.md) e [../README.it.md](../../README.it.md).
- **Come so se una modifica richiede documentazione?** Se tocca avvio, permessi, infrastruttura, API o modello dati, deve riflettersi nella documentazione pertinente.

## Vedi anche

- [../README.it.md](../../README.it.md): vista generale del progetto
- [USO.md](USO.md): gestione e configurazione locale
- [ADMINISTRACION.md](ADMINISTRACION.md): ambito di deployment e amministrazione
- [ARQUITECTURA.md](ARQUITECTURA.md): mappa tecnica del sistema
- [API.md](../es/API.md): riferimento degli endpoint

## Avvio consigliato

Per iniziare in un ambiente locale:

```bash
cd backend && python -m uvicorn app.main:app --reload
cd frontend && flutter run
```

O, usando gli script del progetto:

```bat
start.bat --dev
```

Il riferimento completo di comandi e profili del progetto è in [HERRAMIENTAS.md](HERRAMIENTAS.md) e in [../README.it.md](../../README.it.md).
