# Documentazione — Clakettes

Questo indice è il punto di ingresso principale della documentazione del progetto. È pensato affinché utenti, amministratori e sviluppatori trovino la guida giusta senza leggere file a caso.

## Lingue

Tutta la documentazione esiste nelle 9 lingue della piattaforma. Lo spagnolo (canario) è canonico:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

## Come navigare nella documentazione

- **Voglio usare l'app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Amministro un deployment** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Sviluppo** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md) + [BACKEND.md](BACKEND.md) + [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md)
- **Riferimento per gli agenti** → i comandi e le convenzioni di sviluppo sono in [../AGENTS.md](../../AGENTS.md)

## Principi della documentazione

- **Un solo documento canonico per argomento**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) e [API.md](API.md) sono il riferimento ufficiale del loro ambito.
- **Documentazione per pubblico**: ogni guida è scritta per un tipo di lettore, non per un solo insieme di comandi.
- **Link diretti**: da qui i contenuti rilevanti sono a meno di un clic.
- **Nessuna duplicazione inutile**: i documenti secondari rimandano al canonico invece di ripeterlo.

## Indice dei documenti

| Documento | Cosa copre | Pubblico |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Utilità reale per ruolo e flussi (festival, iscrizione, comitati, premi, chat/E2EE, voto della giuria) | utente, admin |
| [USO.md](USO.md) | Avvio, variabili, migrazione SQLite↔MariaDB, backup, ruoli e gestione | utente, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoint `/api/admin`, account iniziale, rotazione dei segreti, limiti, risoluzione problemi | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Profili Docker, porte, volumi, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Token, matrice `require_*`, perimetro, checklist produzione | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Mappa del sistema + regole backend/frontend + flussi chiave | dev |
| [API.md](API.md) | Riferimento degli endpoint | dev |
| [DESARROLLO.md](DESARROLLO.md) | Convenzione per aggiungere endpoint/schermata + gate CI | dev |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Script `start.*`, build distribuibili, Docker, fix CI | dev |
| [PUSH.md](PUSH.md) | Decisione notifiche senza Firebase | dev |
| [DATABASE.md](DATABASE.md) | Schema doppio SQLite/MariaDB, schede per modello, ER | dev |
| [BACKEND.md](BACKEND.md) | Guida del backend (livelli, config, auth, test) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Rapporto di audit (rev. 10/10/2026) | riferimento |
| [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md) | Protocollo di federazione tra nodi (fasi 2 a 10) | dev |
| [FEDERATION_SCHEMA.md](FEDERATION_SCHEMA.md) | Clakettes Schema v1 (entità federate minime) | dev |
| [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) | Modello di fiducia federato, mTLS, manifesto firmato, portabilità, chat e resilienza | dev |
| [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md) | Decisione sul broker (NATS JetStream) per chat ed eventi tra nodi; WebSocket di bordo e fallback mononodo | dev |

## Percorso consigliato per profilo

### Utente finale

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) solo se devono verificare i permessi o l'ambiente di produzione

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
7. [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md)
8. [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md)
9. [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md)

## Convenzioni per mantenere la documentazione

- Aggiorna il documento canonico prima di qualsiasi riassunto o indice.
- Se cambi un flusso di avvio, sincronizza [README.md](../../README.md), [USO.md](USO.md) e [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Se cambi un'API pubblica, aggiorna [API.md](API.md) e, se opportuno, [DESARROLLO.md](DESARROLLO.md).
- Se cambi lo schema o la persistenza, verifica [DATABASE.md](DATABASE.md) e le migrazioni.
- Ogni volta che modifichi un documento in `docs/es/`, replica la modifica nelle 8 sorelle (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## FAQ rapida

- **Da dove inizio?** Leggi [USO.md](USO.md) se gestirai l'app; leggi [ARQUITECTURA.md](ARQUITECTURA.md) se svilupparai.
- **Che cos'è canonico e che cosa no?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) e [DATABASE.md](DATABASE.md) sono il riferimento ufficiale per questi argomenti.
- **Dove trovo un comando o uno script?** Controlla [HERRAMIENTAS.md](HERRAMIENTAS.md) e [../README.md](../../README.md).
- **Come so se una modifica richiede documentazione?** Se riguarda avvio, permessi, infrastruttura, API o modello dati, deve essere riportata nella documentazione pertinente.

## Vedi anche

- [../README.md](../../README.md): panoramica del progetto
- [USO.md](USO.md): gestione e configurazione locale
- [ADMINISTRACION.md](ADMINISTRACION.md): ambito di deployment e amministrazione
- [ARQUITECTURA.md](ARQUITECTURA.md): mappa tecnica del sistema
- [API.md](API.md): riferimento degli endpoint
