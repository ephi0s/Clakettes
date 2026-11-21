# Erabilera — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Abiarazte azkarra

| Nahi dut | Komandoa |
|---|---|
| Dena lokalean | `.\start.ps1` edo `./start.sh` (Docker badago, lokala bestela) |
| Soilik backend / frontend | `-NoFrontend` / `-NoBackend` |
| Nabigatzailean probatu | `-Web` (modu lokala) |
| Tokiko ekoizpena | `-Final` (web build + serve) |
| Testak | `-TestBackend` / `-TestFrontend` |
| Migrazioak / MariaDBrekin | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Dena gelditu | `-Kill` |
| Falta diren mendekotasunak instalatu | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: SOaren kudeatzailea + git clone) |
| Ingurunea abiarazi gabe berrikusi | `-Check` (doctor: Docker, Python, Flutter, .venv, atak; 1 itzultzen da zerbait falta bada) |
| Banaketarako build-ak | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Docker gabe, abiarazleak tokiko ingurune bare-metal bat sortzen du: Python 3.12+ eta Flutter detektatzen ditu, nola instalatu erakusten du zure SOaren arabera eta `-InstallMissing` bidez instalatzea eskaintzen du (galdetu egin du flag-arekin ez bazabiltza).

Dev URLak: backend `http://localhost:8000` (Swagger `/docs`-en), frontend `http://localhost:3000`.
Ataka okupatuta badago, berez bir esleitzen da (begiratu `[PUERTO]` irteeran).
Hasierako admin-a (soilik ekoizpenean ez): `admin` / `setup` — sartzean aldatu.

## Konfigurazioa

| Aldagaia / flag-a | Non | Eragina |
|---|---|---|
| `BACKEND_URL` | `--dart-define` edo app-eko backend-pantaila | APIaren URLa (SharedPreferences-en irauten du) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; Docker-en `./data/clakettes.db`) edo `mariadb+pymysql://…?ssl_ca=…` (prod, TLS nahitaezkoa) |
| `SECRET_KEY` | env (nahitaezkoa `APP_ENV=production`-en) | JWT sinadura; default seguruak prod-eko abiaraztea blokeatzen du |
| `CORS_ORIGINS` | env | Jatorri esplizituak prod-en (`*` debekatuta kredentzialekin) |
| `APP_ENV` | env | `development`-ek admin + `create_all` sortzen ditu; `production`-ek Alembic eskatzen du |
| `PUBLIC_BASE_URL` | `backend/.env` | Nodoaren domeinu publikoa; manifestuan eta portabilitate-bundle-etan agertzen da |
| `MTLS_REQUIRED` | env | Egiaztatutako pare mTLSa behartzen du federazioan (ziurtagiriaren CNa eta PEMa) |
| `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | env | Manifestua sinatzen duten ziurtagiriaren PEMa eta gako pribatua (RSA-SHA256) |

## Operazioa

- **Migratu**: `alembic upgrade head` `backend/`-tik (Docker: `-Migrate`).
- **Migrazio automatikoa**: aplikazioak DB-a berez migratzen du abiaraztean eta DB berriak unearen berrikuspenarekin zigilatzen ditu; `SKIP_AUTO_MIGRATE=1` saltzeko (kanpoan kudeatutako DBentzat).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; itzulera `import_mariadb_to_sqlite.py` bidez (xehetasuna [DATABASE.md](DATABASE.md) fitxategian).
- **Babeskopiak**: SQLite = `*.db` kopiatu; MariaDB = `mariadb-dump` (Docker-en `db-data` bolumena).
- **Logak**: uvicorn stdout (DAV tokenak dagoeneko ezkutatuta); API erroreak SnackBar + `debugPrint` bidez.
- **Mugak**: gorputzak ≤10 MB (413 handiagoa bada); rate limit 429 + birsaioarekin (federazioa 60/60 s IP bakoitzeko; txata 10/60 s nodo eta erabiltzaile bakoitzeko, `TESTING=true` bidez desaktibatuta).
- **Federazioa**: egiaztatu hirugarren nodo bat `python tools/federation_conformance.py <url> [--json]` bidez; peering-aren osasuna `/api/federation/resilience/health`-en dago eta p50/p95 metrikak `/metrics`-en.
- **Portabilitatea**: esportatu/inportatu bundle-ak `/api/federation/portability/{bundles,imports}` bidez eta kontsultatu identitate-birbideratzeak `/redirects/{ref}` bidez.

## Erabiltzaile-rolak

`admin` (guztia) → `organizer` (bere jaialdia: gertaerak, formularioak, batzordeak) → `attendee`/`juror`/etab. (organizer-ek esleituta; auto-join-ek soilik `attendee` ematen du). Kanalak: `admin`/`moderator`/`member`; batzordeak kide-kopuruarekin zerrendan.

## Garapen aktiboko funtzioak

🚧 Honako funtzioak garapen aktiboan daude eta alda daitezke:

- **Profil sozialak**: argitalpen-hormak (Markdown-ekin eta bideo eta podcast txertaketekin mikroblogintza) erabiltzaile eta jaialdien profilaketan, argitalpen bakoitzeko aukerako erantzun-hariak eta rolekiko moderazioarekin (administratzaileak, jaialdiaren kudeaketa, moderatzaileak). Oraindik ez dago erreakziorik, pegatinarik edo GIF-ik.
- **Profilen pertsonalizazioa**: azala, leloa eta gizarte-loturak erabiltzaile eta jaialdietan.
- **Intsigniak**: lehenespenez desaktibatuta; soilik administrazio-taldeak aktiba ditzake (`PUT /api/badges/settings`). Plataformako intsigniak administratzaileek ematen dituzte; jaialdiaren merituzkoak (beteranoa, ezaguna, rola, sari berezia), haren kudeaketak. Intsignia bakoitzak irudi bat du (SVG hobetsia).
- **Epaimahaiaren botoa**: lan bakoitzeko puntuazioa, agregazioa eta anonimotasun aukerakoa (roadmap-aren 5. fasea).

## Ikus ere

- [README.eu.md](../../README.eu.md): proiektuaren deskribapen orokorra eta sarbide azkarra
- [HERRAMIENTAS.md](HERRAMIENTAS.md): exekuzio-script-ak eta komandoak
- [ADMINISTRACION.md](ADMINISTRACION.md): inplementazioaren administrazioa eta sekretuen birzirkulazioa
- [SEGURIDAD.md](SEGURIDAD.md): kontrol-zerrenda eta ekoizpenerako jardunbide egokiak
