# Erabilitza — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Hasi ziurtuta

| Nirek | K |
|-------|---|
| Baina local | `.\start.ps1` edo `./start.sh` (Docker badago, local bestela) |
| Backend bakarra / frontend bakarra | `-NoFrontend` / `-NoBackend` |
| Web-ko navigatoren barruan prove | `-Web` (modu local) |
| Production-eko local | `-Final` (web-build + serve) |
| Proba | `-TestBackend` / `-TestFrontend` |
| Migratzeko / MariaDB-ekin | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Baina hautatu | `-Kill` |
| Herriarendu installer | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: OS-ko instaloratzaile + git clone) |
| Baina hautatu hasi gabe | `-Check` (doctor: Docker, Python, Flutter, .venv, portuak; 1-ken emaitza aukerakortakoak) |
| Konprezentatutako erasoak | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Docker-rik ez badago, hainbat java eduki hasi izango dugu zerbitzari barretatik. Python 3.12+ eta Flutter detektatzen dugu, SO-n arabera instalatze-gida erakusten dugu, eta `-InstallMissing` flag-kin aukeratu nahi badugu (aurkezten baduzu, hurrengo aipamenan) instalatzea eskaintzen dugu.

Dev URLak: backend `http://localhost:8000` (Swagger `/docs`-en), frontend `http://localhost:3000`.
Port batean baimenduta baduzu, automatikoki berriz salgatzen da (`[PUERTO]` izenekin). Admin hasiera (ez-produkzio zizkean): `admin` / `setup` — aldatu hasiera klikuan.

## Konfigurazioa

| Aldagaia / flag | Non | Emaitza |
|-----------------|-----|---------|
| `BACKEND_URL` | `--dart-define` edo frontend-ko pantalla | API-ren url-a (SharedPreferences-eko konexioa) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (local; Docker-n `./data/clakettes.db`) edo `mariadb+pymysql://…?ssl_ca=…` (produkzioan, TLS beharrezkoa) |
| `SECRET_KEY` | env (produkzioan beharrezkoa `APP_ENV=production`) | JWT-aren finkatu; inseguru default-a blokeatzen du produktu hasieratzean |
| `CORS_ORIGINS` | env | Origen eskalatuta produktu batean (`*` ez da baimenduta credentials-arekin) |
| `APP_ENV` | env | `development` admin-a + `create_all` sortzen du; `production` alembic behar du |

## Etapak

- **Migrate**: `alembic upgrade head` `backend/` no (Docker: `-Migrate`).
- **Automatikoa**: aplikazioa berein DB-ak hasieran migrate egiten du eta zizketek honetan deskriptatzen da; `SKIP_AUTO_MIGRATE=1` hau ez gezetze (DB-k iniheritate anyagak).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; atzera `import_mariadb_to_sqlite.py` (datuak [DATABASE.md](DATABASE.md)-en).
- **Backups**: SQLite = `*.db` kopiatu; MariaDB = `mariadb-dump` (docker-ko `db-data`).
- **Logak**: uvicorn stdout (token DAV redacted); API-ko erroreak SnackBar-ko + `debugPrint`.
- **Limiteak**: eraskaria <=10 MB (413 badago); rate-limit 429 + saiatu berriro.

## Erabiltzaile-rolak

`admin` (dena) → `organizer` (bere festival-a: txarpinak, formulariok, komitetak) → `attendee`/`juror`/etc. (kideak berritzen dituzte; auto-join `attendee` duzu). Txapelketa: `admin`/`moderator`/`member`; komiteetan kide-ken kopurua zerrendatik.

## Prozesuak barru egin daitezkeenak

🚧 Hurrengo prozesuak barru egiten direnak eta aldatu daitezkeenak:

- **Perfil sozialak**: publikatuko murek (Markdown-arekin eta video/podcast-ekoाग embedded-ak) erabiltzailea eta festival-eko profilen barruan, publikatuko bati erantzun batiskarachak (administratzaileak, festival-ko kudeatzaileak, moderatzaileek). Reakzioak, stikerrak edo GIF-ak ez badute oraindik.
- **Perfil-petsatutakoak**: kofratua, tagline eta social-eko linkak erabiltzaile eta festival-koak.
- **Insignak**: ez badago oraindik bateratze; admin-taldeak aukeratu ditzakete (`PUT /api/badges/settings`). Plataforma-ko insignak administratzaileek ematen dituzte; festival-ko merit-ko insignak (vetikoa, populara, pertsona, premio especial), erantzat. Insignak bakoitzak irudia du (SVG-preferiza).
- **Jurado-ko bota**: puntuaketa obra-aren arabera, agregazioa automatiqueki eta anonimatza aukeratu (roadmap-eko 5. fasea).

## Aukerak

- [README.md](../../README.eu.md): proiektuaren oharra eta aukeratutako kidea
- [HERRAMIENTAS.md](HERRAMIENTAS.md): erausiak eta klikatutako komandoak
- [ADMINISTRACION.md](ADMINISTRACION.md): deploiamentuaren eta sekretu-rotailaren kudeaketa
- [SEGURIDAD.md](SEGURIDAD.md): emaitza-oharra eta hornitzeko besteak