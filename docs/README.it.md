# Documentazione — Clakettes

Tutta la documentazione esiste nelle 9 lingue della piattaforma. Lo spagnolo è canonico:
[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Questo indice è l'ingresso principale della documentazione del progetto. È pensato perché un utente, un amministratore o uno sviluppatore trovi la guida giusta senza leggere file a caso.

## Come navigare nella documentazione

- **Voglio usare l'app** → [USO.it.md](USO.it.md) + [FUNCIONAL.it.md](FUNCIONAL.it.md)
- **Amministro un deployment** → [ADMINISTRACION.it.md](ADMINISTRACION.it.md) + [INFRAESTRUCTURA.it.md](INFRAESTRUCTURA.it.md) + [SEGURIDAD.it.md](SEGURIDAD.it.md)
- **Sviluppo** → [ARQUITECTURA.it.md](ARQUITECTURA.it.md) + [DESARROLLO.it.md](DESARROLLO.it.md) + [API.md](API.md) + [DATABASE.it.md](DATABASE.it.md)
- **IA / agente** → [ARQUITECTURA.it.md](ARQUITECTURA.it.md) e il documento del compito; i comandi e le convenzioni obbligatorie sono in [../AGENTS.md](../AGENTS.md)

## Principi della documentazione

- **Un solo documento canonico per tema**: [SEGURIDAD.it.md](SEGURIDAD.it.md), [USO.it.md](USO.it.md), [DATABASE.it.md](DATABASE.it.md) e [API.md](API.md) sono il riferimento ufficiale del loro ambito.
- **Documentazione per pubblico**: ogni guida è scritta per un tipo di lettore, non per un solo insieme di comandi.
- **Link diretti**: da qui si può arrivare al contenuto rilevante in meno di un clic.
- **Senza duplicazione inutile**: i documenti secondari linkano il canonico invece di ripeterlo.

## Indice per documento

| Documento | Qué cubre | Audiencia |
|---|---|---|
| [FUNCIONAL.it.md](FUNCIONAL.it.md) | Utilidad real por rol y flujos (festival, inscripción, comités, premios, chat/E2EE) | usuario, admin, IA |
| [USO.it.md](USO.it.md) | Arranque, variables, migración SQLite↔MariaDB, backups, roles y operación | usuario, admin |
| [ADMINISTRACION.it.md](ADMINISTRACION.it.md) | Endpoints `/api/admin`, cuenta inicial, rotación de secretos, límites, troubleshooting | admin |
| [INFRAESTRUCTURA.it.md](INFRAESTRUCTURA.it.md) | Perfiles Docker, puertos, volúmenes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.it.md](SEGURIDAD.it.md) | Tokens, matriz `require_*`, perímetro, checklist producción | admin, dev |
| [ARQUITECTURA.it.md](ARQUITECTURA.it.md) | Mapa sistema + reglas backend/frontend + flujos clave | dev, IA |
| [API.md](API.md) | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.it.md](DESARROLLO.it.md) | Convención para añadir endpoint/pantalla + puertas CI | dev, IA |
| [HERRAMIENTAS.it.md](HERRAMIENTAS.it.md) | Scripts `start.*`, builds distribuibles, Docker, fixes CI | dev |
| [PUSH.it.md](PUSH.it.md) | Decisión de notificaciones sin Firebase | dev |
| [DATABASE.it.md](DATABASE.it.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| [BACKEND.it.md](BACKEND.it.md) | Guía del backend (capas, config, auth, tests) | dev |
| [AUDITORIA.it.md](AUDITORIA.it.md) | Informe de auditoría (rev. 10/10/2026) | referencia |

## Percorso consigliato per profilo

### Utente finale

1. [USO.it.md](USO.it.md)
2. [FUNCIONAL.it.md](FUNCIONAL.it.md)
3. [SEGURIDAD.it.md](SEGURIDAD.it.md) solo se devono rivedere permessi o ambiente produttivo

### Amministratore del deployment

1. [ADMINISTRACION.it.md](ADMINISTRACION.it.md)
2. [INFRAESTRUCTURA.it.md](INFRAESTRUCTURA.it.md)
3. [SEGURIDAD.it.md](SEGURIDAD.it.md)
4. [USO.it.md](USO.it.md)

### Sviluppatore

1. [../AGENTS.md](../AGENTS.md)
2. [ARQUITECTURA.it.md](ARQUITECTURA.it.md)
3. [DESARROLLO.it.md](DESARROLLO.it.md)
4. [API.md](API.md)
5. [DATABASE.it.md](DATABASE.it.md)

## Convenzioni per mantenere la documentazione

- Aggiorna il documento canonico prima di qualunque riepilogo o indice.
- Se cambi un flusso di avvio, sincronizza [README.it.md](../README.it.md), [USO.it.md](USO.it.md) e [HERRAMIENTAS.it.md](HERRAMIENTAS.it.md).
- Se cambi un'API pubblica, aggiorna [API.md](API.md) e, se del caso, [DESARROLLO.it.md](DESARROLLO.it.md).
- Se cambi lo schema o la persistenza, rivedi [DATABASE.it.md](DATABASE.it.md) e le migrazioni.

## FAQ rapida

- **Da dove comincio?** Leggi [USO.it.md](USO.it.md) se gestirai l'app; leggi [ARQUITECTURA.it.md](ARQUITECTURA.it.md) se svilupperai.
- **Cosa è canonico e cosa no?** [USO.it.md](USO.it.md), [SEGURIDAD.it.md](SEGURIDAD.it.md), [API.md](API.md) e [DATABASE.it.md](DATABASE.it.md) sono il riferimento ufficiale per quei temi.
- **Dove trovo un comando o script?** Controlla [HERRAMIENTAS.it.md](HERRAMIENTAS.it.md) e [../README.it.md](../README.it.md).
- **Come so se una modifica richiede documentazione?** Se tocca avvio, permessi, infrastruttura, API o modello dati, deve riflettersi nella documentazione pertinente.

## Vedi anche

- [../README.it.md](../README.it.md): vista generale del progetto
- [USO.it.md](USO.it.md): gestione e configurazione locale
- [ADMINISTRACION.it.md](ADMINISTRACION.it.md): ambito di deployment e amministrazione
- [ARQUITECTURA.it.md](ARQUITECTURA.it.md): mappa tecnica del sistema
- [API.md](API.md): riferimento degli endpoint

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

Il riferimento completo di comandi e profili del progetto è in [HERRAMIENTAS.it.md](HERRAMIENTAS.it.md) e in [../README.it.md](../README.it.md).
