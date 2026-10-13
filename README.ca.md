# Clakettes

La plataforma on els festivals de cinema viuen tot l'any: convocatòries, curts, equips, seus i públic en un mateix lloc.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

[Español](README.md) · [English](README.en.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Italiano](README.it.md) · [Català](README.ca.md) · [Euskara](README.eu.md) · [Galego](README.gl.md) · [Occitan](README.oc.md)

Funciona en web, Android, iOS i escriptori (Windows, macOS, Linux), en 9 idiomes i també sense connexió.

---

## Per a qui és?

- **Festivals**: publica el teu festival, obre convocatòries, rep curts, organitza comitès i jurats, gestiona seus i comunica el teu palmarès.
- **Professionals del cinema**: crea el teu perfil (direcció, interpretació, so, guió, muntatge, vestuari i més), mostra el teu palmarès i connecta amb festivals i equips.
- **Equips express**: coordina el teu grup de rodatge, geolocalitza participants i presenta el teu curt a concursos express.
- **Públic**: descobreix festivals, segueix curts i contacta amb la comunitat.

## Què pots fer

- **Festivals i convocatòries**: cada festival pot tenir diverses convocatòries obertes amb les seves pròpies regles i formularis d'inscripció.
- **Curts**: puja curtmetratges, vincula'ls a convocatòries i a localitzacions de rodatge.
- **Perfils amb palmarès**: palmarès vinculat a festivals de la plataforma o extern mitjançant enllaços, amb control de privacitat camp per camp.
- **Xat**: missatges directes i de grup o canal per festival, amb xifrat d'extrem a extrem.
- **Mapes**: seus i localitzacions de rodatge en mapes interactius, amb obertura a la teva app de mapes preferida.
- **Sense connexió**: l'app continua funcionant offline i sincronitza els teus canvis en recuperar la connexió.
- **En el teu idioma**: espanyol, anglès, francès, alemany, italià, català, euskera, gallec i occità, amb detecció automàtica.

## Requisits i arrencada

### Requisits mínims

- Python 3.12+
- Flutter SDK >= 3.0.0 y < 4.0.0
- Git
- Docker y Docker Compose para despliegue/entorno productivo
- Navegador amb suport per a web (recomanat Chrome/Brave)

### Inici ràpid

En Windows:

```bat
start.bat --dev
```

En PowerShell:

```powershell
./start.ps1 --dev
```

En Linux/macOS:

```bash
./start.sh --dev
```

Això aixeca el backend a `http://localhost:8000` i l'app en mode local; l'API exposa Swagger/OpenAPI a `/docs`. Pots desactivar qualsevol de les dues parts amb `--no-backend` o `--no-frontend`.

### Altres opcions útils

```bash
start.bat --help
start.bat --migrate
start.bat --build
start.bat --build-all
```

Consulta la referència completa de l'arrencada i desplegament a [docs/HERRAMIENTAS.ca.md](docs/HERRAMIENTAS.ca.md) i [docs/USO.ca.md](docs/USO.ca.md).

## Variables d'entorn i configuració

### Backend

Crea o ajusta `backend/.env` amb almenys:

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
```

Per a entorn productiu s'utilitza MariaDB; els scripts i la documentació de desplegament ho gestionen amb Docker.

### Frontend

L'app reutilitza el backend per URL, normalment amb `--dart-define`:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

L'arrencada automàtica del projecte ja configura això quan s'utilitza `start.*`.

## Estat del projecte

🚧 **En desenvolupament actiu** — Festivals, curts, xat amb E2EE, mapes, mode offline i 9 idiomes funcionant; amb tests en backend (~1400) i frontend (69 fitxers).

**Roadmap proper:**

- [ ] Notificaciones push (Firebase/APNs)
- [ ] AppImage Linux firmado
- [ ] Windows MSI installer
- [x] Documentación API OpenAPI exportable (`/openapi.json` sin operationIds duplicados + `docs/API.md` regenerado)

## Documentació del projecte

El mapa de documentació és a [docs/README.ca.md](docs/README.ca.md). És la millor entrada per a cada tipus d'usuari:

- [docs/USO.ca.md](docs/USO.ca.md): arrencada, operació, entorn i ús diari
- [docs/ADMINISTRACION.ca.md](docs/ADMINISTRACION.ca.md): administració, comptes i desplegament
- [docs/INFRAESTRUCTURA.ca.md](docs/INFRAESTRUCTURA.ca.md): Docker, ports, CI i infra
- [docs/SEGURIDAD.ca.md](docs/SEGURIDAD.ca.md): tokens, polítiques i checklist de producció
- [docs/ARQUITECTURA.ca.md](docs/ARQUITECTURA.ca.md): arquitectura backend/frontend i fluxos clau
- [docs/API.md](docs/API.md): referència d'endpoints
- [docs/DESARROLLO.ca.md](docs/DESARROLLO.ca.md): com afegir endpoints o pantalles
- [docs/BACKEND.ca.md](docs/BACKEND.ca.md): guia del backend (capes, config, auth, tests)
- [docs/DATABASE.ca.md](docs/DATABASE.ca.md): esquema i migracions

A més, el punt de partida per a desenvolupament i convenció de projecte és [AGENTS.md](AGENTS.md).

### Vegeu també

- [docs/README.ca.md](docs/README.ca.md): índex general per audiència
- [docs/HERRAMIENTAS.ca.md](docs/HERRAMIENTAS.ca.md): ordres de build, test i arrencada
- [docs/FUNCIONAL.ca.md](docs/FUNCIONAL.ca.md): ús real del producte per rol

### FAQ ràpida

- **Necessito Docker per començar?** No. L'arrencada local amb `start.*` funciona sense Docker; Docker serveix per a entorn productiu i builds reproduïbles.
- **Què faig si l'API no respon?** Comprova que el backend és executant-se a `http://localhost:8000` i que `/docs` respon.
- **Quin document he de llegir primer?** Si ets usuari, [docs/USO.ca.md](docs/USO.ca.md); si ets desenvolupador, [docs/ARQUITECTURA.ca.md](docs/ARQUITECTURA.ca.md).
- **Com sé si un canvi requereix actualitzar documentació?** Si canvia arrencada, API, rols, permisos, variables d'entorn o esquema, actualitza també la documentació que correspongui.

## Per a desenvolupadors

> Detall complet a [`AGENTS.md`](AGENTS.md) (arquitectura, ordres i convencions) i a l'índex de [`docs/`](docs/README.ca.md) (guies per rol: funcional, ús, administració, infraestructura, seguretat, arquitectura, API).

**D'una ullada**: backend FastAPI en capes (routers → serveis → models SQLAlchemy, SQLite en dev / MariaDB en prod, JWT + refresh, 18 migracions Alembic); frontend Flutter Material 3 amb dark mode (singletons + `setState()` + streams, Hive offline, 24 widgets reutilitzables).

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

## Desenvolupament local

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
flutter run
```

## Desplegament

```bash
docker compose --profile prod up -d
```

Backend + frontend (nginx) + MariaDB. Els builds distribuïts (web, Windows, Linux, Android) es gestionen amb `start.bat --build-all` i el conjunt de scripts de [docs/HERRAMIENTAS.ca.md](docs/HERRAMIENTAS.ca.md).

## Solució de problemes

### El backend no arrenca

- Verifica que Python 3.12+ estigui instal·lat.
- Comprova que `backend/.env` existeix i és vàlid.
- Executa `cd backend && python -m uvicorn app.main:app --reload` per veure l'error real.

### L'app no connecta amb l'API

- Assegura't que el backend és a `http://localhost:8000`.
- Revisa si `BACKEND_URL` s'està passant amb `--dart-define`.
- Comprova que l'API respon a `/docs`.

### Problemes amb bases de dades o migracions

- Utilitza `cd backend && alembic upgrade head`.
- Si canvies de SQLite a MariaDB, revisa [docs/USO.ca.md](docs/USO.ca.md) i [docs/DATABASE.ca.md](docs/DATABASE.ca.md).

### Frontend amb errors de Flutter

- Executa `cd frontend && flutter pub get`.
- Si hi ha problemes de generació de codi, segueix la documentació d'Hive i build_runner a [docs/ARQUITECTURA.ca.md](docs/ARQUITECTURA.ca.md).

## Contribuir

1. Fes un fork del repositori.
2. Crea una branca (`git checkout -b feature/nueva-funcionalidad`).
3. Fes commit amb missatges clars i descriptius (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Empeny la branca (`git push origin feature/nueva-funcionalidad`).
5. Obre un Pull Request amb context, canvis i validació.

**Convencions de qualitat:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` i `flutter test` han de passar abans de fusionar.

## Llicència

Aquest projecte és sota la **Llicència MIT**. Consulta [LICENSE](LICENSE).
