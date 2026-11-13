# Clakettes

La piattaforma dove i festival cinematografici vivono tutto l'anno: bandi, corti, squadre, sedi e pubblico nello stesso luogo.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Funziona su web, Android, iOS e desktop (Windows, macOS, Linux), in 9 lingue e anche senza connessione.

---

## Per chi è?

- **Festival**: pubblica il tuo festival, apri bandi, ricevi corti, organizza comitati e giurie, gestisci sedi e comunica il tuo palmarès.
- **Professionisti del cinema**: crea il tuo profilo (regia, interpretazione, suono, sceneggiatura, montaggio, costumi e altro), mostra il tuo palmarès e connettiti con festival e squadre.
- **Squadre express**: coordina il tuo gruppo di ripresa, geolocalizza i partecipanti e presenta il tuo corto a concorsi express.
- **Pubblico**: scopri festival, segui corti e contatta la comunità.

## Cosa puoi fare

- **Festival e bandi**: ogni festival può avere vari bandi aperti con le proprie regole e form di iscrizione.
- **Corti**: carica cortometraggi, collegali a bandi e a location di ripresa.
- **Profili con palmarès**: palmarès collegato a festival della piattaforma o esterno tramite link, con controllo della privacy campo per campo.
- **Chat**: messaggi diretti e di gruppo o canale per festival, con cifratura end-to-end.
- **Mappe**: sedi e location di ripresa su mappe interattive, con apertura nella tua app di mappe preferita.
- **Senza connessione**: l'app continua a funzionare offline e sincronizza le tue modifiche al recupero della connessione.
- **Nella tua lingua**: spagnolo, inglese, francese, tedesco, italiano, catalano, basco, galiziano e occitano, con rilevamento automatico.

## Requisiti e avvio

### Requisiti minimi

- Python 3.12+
- Flutter SDK >= 3.0.0 y < 4.0.0
- Git
- Docker y Docker Compose para despliegue/entorno productivo
- Navegador con soporte para web (recomendado Chrome/Brave)

### Avvio rapido

In Windows:

```bat
start.bat --dev
```

In PowerShell:

```powershell
./start.ps1 --dev
```

In Linux/macOS:

```bash
./start.sh --dev
```

Questo avvia il backend in `http://localhost:8000` e l'app in modalità locale; l'API espone Swagger/OpenAPI in `/docs`. Puoi disattivare una delle due parti con `--no-backend` o `--no-frontend`.

### Altre opzioni utili

```bash
start.bat --help
start.bat --migrate
start.bat --build
start.bat --build-all
```

Consulta il riferimento completo di avvio e deployment in [docs/it/HERRAMIENTAS.md](docs/it/HERRAMIENTAS.md) e [docs/it/USO.md](docs/it/USO.md).

## Variabili di ambiente e configurazione

### Backend

Crea o adatta `backend/.env` con almeno:

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
```

Per ambiente produttivo si usa MariaDB; gli script e la documentazione di deployment lo gestiscono con Docker.

### Frontend

L'app riusa il backend via URL, normalmente con `--dart-define`:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

L'avvio automatico del progetto già configura questo quando si usa `start.*`.

## Stato del progetto

🚧 **In sviluppo attivo** — Festival, corti, chat con E2EE, mappe, modalità offline e 9 lingue funzionanti; con test backend (~1400) e frontend (75 file di test).

**Roadmap successiva:**

- [ ] Notifiche push (Firebase/APNs)
- [ ] AppImage Linux firmato
- [ ] Installaer Windows MSI
- [x] Documentazione OpenAPI esportabile (`/openapi.json` senza operationIds duplicati + `docs/it/API.md` rigenerato)

## Documentazione del progetto

La mappa della documentazione è in [docs/it/README.md](docs/it/README.md). È il miglior ingresso per ogni tipo di utente:

- [docs/it/USO.md](docs/it/USO.md): avvio, operazione, ambiente e uso quotidiano
- [docs/it/ADMINISTRACION.md](docs/it/ADMINISTRACION.md): amministrazione, account e deployment
- [docs/it/INFRAESTRUCTURA.md](docs/it/INFRAESTRUCTURA.md): Docker, porte, CI e infrastruttura
- [docs/it/SEGURIDAD.md](docs/it/SEGURIDAD.md): token, politiche e checklist di produzione
- [docs/it/ARQUITECTURA.md](docs/it/ARQUITECTURA.md): architettura backend/frontend e flussi chiave
- [docs/it/API.md](docs/it/API.md): riferimento degli endpoint
- [docs/it/DESARROLLO.md](docs/it/DESARROLLO.md): come aggiungere endpoint o schermate
- [docs/it/BACKEND.md](docs/it/BACKEND.md): guida del backend (livelli, configurazione, auth, test)
- [docs/it/DATABASE.md](docs/it/DATABASE.md): schema e migrazioni
- [docs/it/FEDERATION_PROTOCOL.md](docs/it/FEDERATION_PROTOCOL.md): protocollo di federazione (fase 4)
- [docs/it/FEDERATION_SCHEMA.md](docs/it/FEDERATION_SCHEMA.md): Clakettes Schema v1
- [docs/it/FEDERATION_SECURITY.md](docs/it/FEDERATION_SECURITY.md): modello di fiducia federato
- [docs/it/PUSH.md](docs/it/PUSH.md): decisione notifiche push

Inoltre, il punto di partenza per sviluppo e convenzione di progetto è [AGENTS.md](AGENTS.md).

### Vedi anche

- [docs/it/README.md](docs/it/README.md): indice generale per pubblico
- [docs/it/HERRAMIENTAS.md](docs/it/HERRAMIENTAS.md): comandi di build, test e avvio
- [docs/it/FUNCIONAL.md](docs/it/FUNCIONAL.md): uso reale del prodotto per ruolo

### FAQ rapida

- **Ho bisogno di Docker per iniziare?** No. L'avvio locale con `start.*` funziona senza Docker; Docker serve per ambiente di produzione e build riproducibili.
- **Cosa faccio se l'API non risponde?** Verifica che il backend sia in esecuzione su `http://localhost:8000` e che `/docs` risponda.
- **Quale documento devo leggere per primo?** Se sei un utente, [docs/it/USO.md](docs/it/USO.md); se sei uno sviluppatore, [docs/it/ARQUITECTURA.md](docs/it/ARQUITECTURA.md).
- **Come faccio a sapere se un cambio richiede aggiornamento documentazione?** Se cambiano avvio, API, ruoli, permessi, variabili d'ambiente o schema, aggiorna anche la documentazione corrispondente.

## Per sviluppatori

> Dettaglio completo in [`AGENTS.md`](AGENTS.md) (architettura, comandi e convenzioni) e nell'indice di [`docs/`](docs/it/README.md) (guide per ruolo: funzionale, uso, amministrazione, infrastruttura, sicurezza, architettura, API).

**A colpo d'occhio**: backend FastAPI a livelli (router → servizi → modelli SQLAlchemy, SQLite in dev / MariaDB in prod, JWT + refresh, 36 migrazioni Alembic); frontend Flutter Material 3 con dark mode (singleton + `setState()` + streams, Hive offline, 32 widget riutilizzabili).

```bash
# Tests
cd backend && python -m pytest tests/ -x -q --tb=short
cd frontend && flutter test

# Lint
cd backend && ruff check . && ruff format --check .
cd frontend && flutter analyze

# Migraciones
cd backend && alembic upgrade head
```

## Sviluppo locale

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
flutter run
```

## Deployment

```bash
docker compose --profile prod up -d
```

Backend + frontend (nginx) + MariaDB. Le build distribuite (web, Windows, Linux, Android) si gestiscono con `start.bat --build-all` e l'insieme di script di [docs/it/HERRAMIENTAS.md](docs/it/HERRAMIENTAS.md).

## Risoluzione dei problemi

### Il backend non si avvia

- Verifica che Python 3.12+ sia installato.
- Controlla che `backend/.env` esista e sia valido.
- Esegui `cd backend && python -m uvicorn app.main:app --reload` per vedere l'errore reale.

### L'app non si connette all'API

- Assicurati che il backend sia su `http://localhost:8000`.
- Controlla se `BACKEND_URL` viene passato con `--dart-define`.
- Verifica che l'API risponda su `/docs`.

### Problemi con database o migrazioni

- Usa `cd backend && alembic upgrade head`.
- Se passi da SQLite a MariaDB, controlla [docs/it/USO.md](docs/it/USO.md) e [docs/it/DATABASE.md](docs/it/DATABASE.md).

### Frontend con errori di Flutter

- Esegui `cd frontend && flutter pub get`.
- Se ci sono problemi di generazione del codice, segui la documentazione di Hive e build_runner in [docs/it/ARQUITECTURA.md](docs/it/ARQUITECTURA.md).

## Contribuire

1. Fai un fork del repository.
2. Crea un ramo (`git checkout -b feature/nuova-funzionalità`).
3. Fai commit con messaggi chiari e descrittivi (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Spingi il ramo (`git push origin feature/nuova-funzionalità`).
5. Apri una Pull Request con contesto, modifiche e validazione.

**Convenzioni di qualità:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` e `flutter test` devono passare prima del merge.

## Licenza

Questo progetto è sotto la **Licenza MIT**. Consulta [LICENSE](LICENSE).
