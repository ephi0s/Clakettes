# Clakettes

Zine-jaialdiak urte osoan bizi diren plataforma: deialdiak, laburrak, ekipoak, egoitzak eta publikoa leku berean.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

[Español](README.md) · [English](README.en.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Italiano](README.it.md) · [Català](README.ca.md) · [Euskara](README.eu.md) · [Galego](README.gl.md) · [Occitan](README.oc.md)

Web-ean, Android-en, iOS-en eta escritorioan funtzionatzen du (Windows, macOS, Linux), 9 hizkuntzatan eta konexiorik gabe ere.

---

## Norentzat da?

- **Jaialdiak**: argitaratu zure jaialdia, ireki deialdiak, jaso laburrak, antolatu batzordeak eta epaimahaiak, kudeatu egoitzak eta komunikatu zure palmaresa.
- **Zineko profesionalak**: sortu zure profila (zuzendaritza, interpretazioa, soinua, gidoia, muntaia, jantziak eta gehiago), erakutsi zure palmaresa eta konektatu jaialdi eta ekipoekin.
- **Ekipo express-ak**: koordinatu zure errodaje-taldea, geolokalizatu parte-hartzaileak eta aurkeztu zure laburra express lehiaketetara.
- **Publikoa**: deskubritu jaialdiak, jarraitu laburrak eta kontaktatu komunitatearekin.

## Zer egin dezakezu

- **Jaialdiak eta deialdiak**: jaialdi bakoitzak hainbat deialdi ireki izan ditzake bere arau eta izen-emate inprimakiekin.
- **Laburrak**: igo laburmetraiak, lotu deialdi eta errodaje-kokapenetara.
- **Palmares-dun profilak**: plataformako jaialdiei lotutako edo kanpo-estekazko palmaresa, eremuz eremuko pribatutasun-kontrolarekin.
- **Txata**: mezu zuzenak eta talde/kanalekoak jaialdiko, muturretik muturrerako zifraketarekin.
- **Mapak**: egoitzak eta errodaje-kokapenak mapa interaktiboetan, zure mapa-app gogokoenean irekitzeko aukerarekin.
- **Konexiorik gabe**: app-ak offline funtzionatzen jarraitzen du eta zure aldaketak sinkronizatzen ditu konexioa berreskuratzean.
- **Zure hizkuntzan**: gaztelania, ingelesa, frantsesa, alemana, italiera, katalana, euskara, galegoa eta okzitaniera, detekzio automatikoarekin.

## Baldintzak eta abiaraztea

### Gutxieneko baldintzak

- Python 3.12+
- Flutter SDK >= 3.0.0 eta < 4.0.0
- Git
- Docker eta Docker Compose hedapen/ingurune produktiborako
- Web-erako euskarri-dun nabigatzailea (gomendatua Chrome/Brave)

### Hasiera azkarra

Windows-en:

```bat
start.bat --dev
```

PowerShell-en:

```powershell
./start.ps1 --dev
```

Linux/macOS-en:

```bash
./start.sh --dev
```

Honek backend-a `http://localhost:8000`-n eta app-a modu lokalean altxatzen ditu; API-k Swagger/OpenAPI erakusten du `/docs`-en. Bi zatietako edozein desaktibatu dezakezu `--no-backend` edo `--no-frontend`-ekin.

### Beste aukera erabilgarri batzuk

```bash
start.bat --help
start.bat --migrate
start.bat --build
start.bat --build-all
```

Kontsultatu abiarazte eta hedapenaren erreferentzia osoa [docs/HERRAMIENTAS.md](docs/HERRAMIENTAS.eu.md)-n eta [docs/USO.md](docs/USO.eu.md)-n.

## Ingurune-aldagaiak eta konfigurazioa

### Backend-a

Sortu edo doitu `backend/.env` gutxienez honekin:

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
```

Ingurune produktiborako MariaDB erabiltzen da; script-ek eta hedapen-dokumentazioak Docker-ekin kudeatzen dute.

### Frontend-a

App-ak backend-a URL bidez berrerabiltzen du, normalean `--dart-define`-ekin:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

Proiektuaren abiarazte automatikoak hau jada konfiguratzen du `start.*` erabiltzean.

## Proiektuaren egoera

🚧 **Garapen aktiboan** — Jaialdiak, laburrak, E2EE-dun txata, mapak, offline modua eta 9 hizkuntza funtzionatzen; test-ekin backend-ean (~1400) eta frontend-ean (69 fitxategi).

**Hurrengo roadmap-a:**

- [ ] Push jakinarazpenak (Firebase/APNs)
- [ ] Sinatutako Linux AppImage
- [ ] Windows MSI installer
- [x] Dokumentazio API OpenAPI esportagarria (`/openapi.json` operationId bikoiztu gabe + `docs/API.md` birsortua)

## Proiektuaren dokumentazioa

Dokumentazio-mapa [docs/README.md](docs/README.eu.md)-n dago. Sarrera onena da erabiltzaile-mota bakoitzerako:

- [docs/USO.md](docs/USO.eu.md): abiaraztea, operazioa, ingurunea eta eguneroko erabilera
- [docs/ADMINISTRACION.md](docs/ADMINISTRACION.eu.md): administrazioa, kontuak eta hedapena
- [docs/INFRAESTRUCTURA.md](docs/INFRAESTRUCTURA.eu.md): Docker, portuak, CI eta azpiegitura
- [docs/SEGURIDAD.md](docs/SEGURIDAD.eu.md): token-ak, politikak eta ekoizpen-checklist-a
- [docs/ARQUITECTURA.md](docs/ARQUITECTURA.eu.md): backend/frontend arkitektura eta funtsezko fluxuak
- [docs/API.md](docs/API.md): endpoint-en erreferentzia
- [docs/DESARROLLO.md](docs/DESARROLLO.eu.md): endpoint-ak edo pantailak nola gehitu
- [docs/BACKEND.md](docs/BACKEND.eu.md): backend-aren gida (geruzak, config, auth, test-ak)
- [docs/DATABASE.md](docs/DATABASE.eu.md): eskema eta migrazioak

Gainera, garapenerako eta proiektu-konbentziorako abiapuntua [AGENTS.md](AGENTS.md) da.

### Ikusi halaber

- [docs/README.md](docs/README.eu.md): audientziako indize orokorra
- [docs/HERRAMIENTAS.md](docs/HERRAMIENTAS.eu.md): build, test eta abiarazte komandoak
- [docs/FUNCIONAL.md](docs/FUNCIONAL.eu.md): produktuaren benetako erabilera rolez

### FAQ azkarra

- **Docker behar dut hasteko?** Ez. `start.*`-rekin tokiko abiaraztea Docker gabe funtzionatzen du; Docker ingurune produktiborako eta build erreproduzigarrietarako da.
- **Zer egin API-k erantzuten ez badu?** Egiaztatu backend-a `http://localhost:8000`-n martxan dagoela eta `/docs`-ek erantzuten duela.
- **Zer dokumentu irakurri behar dut lehenik?** Erabiltzailea bazara, [docs/USO.md](docs/USO.eu.md); garatzailea bazara, [docs/ARQUITECTURA.md](docs/ARQUITECTURA.eu.md).
- **Nola jakin aldaketa batek dokumentazioa eguneratzea behar duen?** Abiaraztea, API, rolak, baimenak, ingurune-aldagaiak edo eskema aldatzen badu, eguneratu dagokion dokumentazioa ere.

## Garatzaileentzat

> Xehetasun osoa [`AGENTS.md`](AGENTS.md)-n (arkitektura, komandoak eta konbentzioak) eta [`docs/`](docs/README.eu.md)-ko indizean (rol-gidak: funtzionala, erabilera, administrazioa, azpiegitura, segurtasuna, arkitektura, API).

**Begirada batean**: FastAPI backend-a geruzatan (router-ak → zerbitzuak → SQLAlchemy modeloak, SQLite dev-ean / MariaDB prod-ean, JWT + refresh, 18 Alembic migrazio); Flutter frontend-a Material 3 dark mode-arekin (singleton-ak + `setState()` + stream-ak, Hive offline, 24 widget berrerabilgarri).

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

## Tokiko garapena

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
flutter run
```

## Hedapena

```bash
docker compose --profile prod up -d
```

Backend + frontend (nginx) + MariaDB. Build banatuak (web, Windows, Linux, Android) `start.bat --build-all`-ekin eta [docs/HERRAMIENTAS.md](docs/HERRAMIENTAS.eu.md)-ko script-multzoarekin kudeatzen dira.

## Arazoen konponbidea

### Backend-ak ez du abiatzen

- Egiaztatu Python 3.12+ instalatuta dagoela.
- Egiaztatu `backend/.env` existitzen dela eta baliozkoa dela.
- Exekutatu `cd backend && python -m uvicorn app.main:app --reload` benetako errorea ikusteko.

### App-a ez da API-ra konektatzen

- Ziurtatu backend-a `http://localhost:8000`-n dagoela.
- Berrikusi `BACKEND_URL` `--dart-define`-ekin pasatzen ari den.
- Egiaztatu API-k `/docs`-en erantzuten duela.

### Datu-base edo migrazio arazoak

- Erabili `cd backend && alembic upgrade head`.
- SQLite-tik MariaDB-ra aldatzen bazara, berrikusi [docs/USO.md](docs/USO.eu.md) eta [docs/DATABASE.md](docs/DATABASE.eu.md).

### Erroreak dituen Flutter frontend-a

- Exekutatu `cd frontend && flutter pub get`.
- Kode-sorkuntza arazoak badaude, jarraitu Hive eta build_runner dokumentazioa [docs/ARQUITECTURA.md](docs/ARQUITECTURA.eu.md)-n.

## Laguntzea

1. Egin fork errepositorioan.
2. Sortu adar bat (`git checkout -b feature/nueva-funcionalidad`).
3. Egin commit mezu argi eta deskribatzaileekin (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Bultzatu adarra (`git push origin feature/nueva-funcionalidad`).
5. Ireki Pull Request testuinguru, aldaketa eta balidazioarekin.

**Kalitate-konbentzioak:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` eta `flutter test` fusionatu aurretik pasa behar dute.

## Lizentzia

Proiektu hau **MIT Lizentzia** pean dago. Kontsultatu [LICENSE](LICENSE).
