# Documentazione — Clakettes

Questo indice è il punto di ingresso principale della documentazione del progetto. È pensato affinché utenti, amministratori e sviluppatori trovino la guida giusta senza leggere file a caso.

## Lingue

Tutta la documentazione esiste nelle 9 lingue della piattaforma. Lo spagnolo (canario) è canonico:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

## Come navigare nella documentazione

- **Voglio usare l'app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Gestisco un deployment** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Sviluppo** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md) + [BACKEND.md](BACKEND.md)
- **IA / agente** → [ARQUITECTURA.md](ARQUITECTURA.md) e il documento del task; i comandi e le convenzioni obbligatori sono in [../AGENTS.md](../../AGENTS.md)

## Principi della documentazione

- **Un solo documento canonico per tema**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) e [API.md](API.md) sono il riferimento ufficiale per il loro ambito.
- **Documentazione per audience**: ogni guida è scritta per un tipo di lettore, non per un singolo insieme di comandi.
- **Link diretti**: da qui il contenuto rilevante è a meno di un clic di distanza.
- **Nessuna duplicazione inutile**: i documenti secondari si collegano al canonico invece di ripeterlo.

## Indice per documento

| Documento | Cosa copre | Audience |
|-----------|------------|----------|
| [FUNCIONAL.md](FUNCIONAL.md) | Valore reale per ruolo e flussi (festival, iscrizione, comitati, premi, chat/E2EE, voto giuria) | utente, admin, IA |
| [USO.md](USO.md) | Avvio, variabili, migrazione SQLite↔MariaDB, backup, ruoli, operazione | utente, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoint `/api/admin`, conto iniziale, rotazione segreti, limiti, troubleshooting | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Profili Docker, porte, volumi, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Token, matrice `require_*`, perimetro, checklist produzione | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Mappa sistema + regole backend/frontend + flussi chiave | dev, IA |
| [API.md](API.md) | Riferimento endpoint (rigenerabile con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.md](DESARROLLO.md) | Convenzione per aggiungere endpoint/screen + porte CI | dev, IA |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Script `start.*`, build distribuibili, Docker, fix CI | dev |
| [PUSH.md](PUSH.md) | Decisione notifiche senza Firebase | dev |
| [DATABASE.md](DATABASE.md) | Schema duale SQLite/MariaDB, schede per modello, ER | dev, IA |
| [BACKEND.md](BACKEND.md) | Guida backend (layer, config, auth, test) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Report di audit (rev. 10/10/2026) | riferimento |
| [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md) | Protocollo di federazione tra nodi (fase 4) | dev, IA |
| [FEDERATION_SCHEMA.md](FEDERATION_SCHEMA.md) | Clakettes Schema v1 (entità federate minime) | dev, IA |
| [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) | Modello di fiducia federato, mTLS, rotazione certificati | dev, IA |

## Percorso consigliato per profilo

### Utente finale

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) solo se necessario rivedere permessi o ambiente di produzione

### Amministratore di deployment

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Sviluppatore

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.md](API.md)
5. [DATABASE.md](DATABASE.md)
6. [BACKEND.md](BACKEND.md)

## Convenzioni per mantenere la documentazione

- Aggiorna il documento canonico prima di ogni riassunto o indice.
- Se cambi un flusso di avvio, sincronizza [README.it.md](../../README.it.md), [USO.md](USO.md) e [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Se cambi un'API pubblica, aggiorna [API.md](API.md) e, se applicabile, [DESARROLLO.md](DESARROLLO.md).
- Se cambi lo schema o la persistenza, rivedi [DATABASE.md](DATABASE.md) e le migrazioni.
- Quando modifichi un documento in `docs/es/`, replica il cambiamento alle 8 sorelle (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## FAQ veloce

- **Da dove inizio?** Leggi [USO.md](USO.md) se gestisci l'app; leggi [ARQUITECTURA.md](ARQUITECTURA.md) se sviluppi.
- **Cosa è canonico e cosa no?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) e [DATABASE.md](DATABASE.md) sono il riferimento ufficiale per questi temi.
- **Dove trovo un comando o script?** Controlla [HERRAMIENTAS.md](HERRAMIENTAS.md) e [../README.md](../../README.it.md).
- **Come so se un cambiamento richiede documentazione?** Se influenza avvio, permessi, infrastruttura, API o modello dati, deve essere riflesso nella documentazione pertinente.

## Vedi anche

- [../README.it.md](../../README.it.md): panoramica del progetto
- [USO.md](USO.md): operazione e configurazione locale
- [ADMINISTRACION.md](ADMINISTRACION.md): ambito di deployment e amministrazione
- [ARQUITECTURA.md](ARQUITECTURA.md): mappa tecnica del sistema
- [API.md](API.md): riferimento endpoint

## Avvio consigliato

Per iniziare in ambiente locale:

```bash
cd backend && python -m uvicorn app.main:app --reload
cd frontend && flutter run
```

Oppure usando gli script del progetto:

```bat
start.bat --dev
```

La riferimento completa di comandi e profili è in [HERRAMIENTAS.md](HERRAMIENTAS.md) e in [../README.md](../../README.it.md).