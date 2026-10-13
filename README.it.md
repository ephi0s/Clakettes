# Clakettes

La piattaforma dove i festival cinematografici vivono tutto l'anno: bandi, corti, squadre, sedi e pubblico nello stesso luogo.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

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

Consulta il riferimento completo di avvio e deployment in [docs/HERRAMIENTAS.it.md](docs/HERRAMIENTAS.it.md) e [docs/USO.it.md](docs/USO.it.md).

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

🚧 **In sviluppo attivo** — Festival, corti, chat con E2EE, mappe, modalità offline e 9 lingue funzionanti; con test nel backend (~1400) e frontend (69 file).

**Roadmap prossima:**

- [ ] Notificaciones push (Firebase/APNs)
- [ ] AppImage Linux firmado
- [ ] Windows MSI installer
- [x] Documentación API OpenAPI exportable (`/openapi.json` sin operationIds duplicados + `docs/API.md` regenerado)

## Documentazione del progetto

La mappa della documentazione è in [docs/README.it.md](docs/README.it.md). È il miglior ingresso per ogni tipo di utente:

- [docs/USO.it.md](docs/USO.it.md): avvio, gestione, ambiente e uso quotidiano
- [docs/ADMINISTRACION.it.md](docs/ADMINISTRACION.it.md): amministrazione, account e deployment
- [docs/INFRAESTRUCTURA.it.md](docs/INFRAESTRUCTURA.it.md): Docker, porte, CI e infra
- [docs/SEGURIDAD.it.md](docs/SEGURIDAD.it.md): token, policy e checklist di produzione
- [docs/ARQUITECTURA.it.md](docs/ARQUITECTURA.it.md): architettura backend/frontend e flussi chiave
- [docs/API.md](docs/API.md): riferimento degli endpoint
- [docs/DESARROLLO.it.md](docs/DESARROLLO.it.md): come aggiungere endpoint o schermate
- [docs/BACKEND.it.md](docs/BACKEND.it.md): guida del backend (livelli, config, auth, test)
- [docs/DATABASE.it.md](docs/DATABASE.it.md): schema e migrazioni

Inoltre, il punto di partenza per sviluppo e convenzione di progetto è [AGENTS.md](AGENTS.md).

### Vedi anche

- [docs/README.it.md](docs/README.it.md): indice generale per pubblico
- [docs/HERRAMIENTAS.it.md](docs/HERRAMIENTAS.it.md): comandi di build, test e avvio
- [docs/FUNCIONAL.it.md](docs/FUNCIONAL.it.md): uso reale del prodotto per ruolo

### FAQ rapida

- **¿Necesito Docker para empezar?** No. El arranque local con `start.*` funciona sin Docker; Docker sirve para entorno productivo y builds reproducibles.
- **¿Qué hago si la API no responde?** Comprueba que el backend está corriendo en `http://localhost:8000` y que `/docs` responde.
- **¿Qué documento debo leer primero?** Si eres usuario, [docs/USO.it.md](docs/USO.it.md); si eres desarrollador, [docs/ARQUITECTURA.it.md](docs/ARQUITECTURA.it.md).
- **¿Cómo sé si un cambio requiere actualizar documentación?** Si cambia arranque, API, roles, permisos, variables de entorno o esquema, actualiza también la documentación que corresponda.

## Per sviluppatori

> Dettaglio completo in [`AGENTS.md`](AGENTS.md) (architettura, comandi e convenzioni) e nell'indice di [`docs/`](docs/README.it.md) (guide per ruolo: funzionale, uso, amministrazione, infrastruttura, sicurezza, architettura, API).

**A colpo d'occhio**: backend FastAPI a livelli (router → servizi → modelli SQLAlchemy, SQLite in dev / MariaDB in prod, JWT + refresh, 18 migrazioni Alembic); frontend Flutter Material 3 con dark mode (singleton + `setState()` + streams, Hive offline, 24 widget riutilizzabili).

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

Backend + frontend (nginx) + MariaDB. Le build distribuite (web, Windows, Linux, Android) si gestiscono con `start.bat --build-all` e l'insieme di script di [docs/HERRAMIENTAS.it.md](docs/HERRAMIENTAS.it.md).

## Risoluzione dei problemi

### Il backend non si avvia

- Verifica che Python 3.12+ esté instalado.
- Comprueba que `backend/.env` existe y es válido.
- Ejecuta `cd backend && python -m uvicorn app.main:app --reload` para ver el error real.

### L'app non si connette all'API

- Asegúrate de que el backend está en `http://localhost:8000`.
- Revisa si `BACKEND_URL` se está pasando con `--dart-define`.
- Comprueba que la API responde en `/docs`.

### Problemi con database o migrazioni

- Usa `cd backend && alembic upgrade head`.
- Si cambias de SQLite a MariaDB, revisa [docs/USO.it.md](docs/USO.it.md) y [docs/DATABASE.it.md](docs/DATABASE.it.md).

### Frontend con errori di Flutter

- Ejecuta `cd frontend && flutter pub get`.
- Si hay problemas de generación de código, sigue la documentación de Hive y build_runner en [docs/ARQUITECTURA.it.md](docs/ARQUITECTURA.it.md).

## Contribuire

1. Haz un fork del repositorio.
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`).
3. Haz commit con mensajes claros y descriptivos (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Empuja la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request con contexto, cambios y validación.

**Convenciones de calidad:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` y `flutter test` deben pasar antes de fusionar.

## Licenza

Questo progetto è sotto la **Licenza MIT**. Consulta [LICENSE](LICENSE).
