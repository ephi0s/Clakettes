# Clakettes

La plataforma ont los festivals de cinèma vivon tota l'annada: convocatòrias, corts, equipas, sèts e public dins un meteis luòc.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Fonciona en web, Android, iOS e escritòri (Windows, macOS, Linux), en 9 lengas e tanben sens connexion.

---

## Per qui es?

- **Festivals**: publica ton festivau, dubrís convocatòrias, recep corts, organiza comitats e jurats, gerís sèts e comunica ton palmarés.
- **Professionaus del cinèma**: crea ton perfil (direccion, interpretacion, son, guion, montatge, vestuari e mai), mòstra ton palmarés e connecta amb festivals e equipas.
- **Equipas exprèss**: coordina ton grop de rodatge, geolocaliza los participants e presenta ton cort als concorses exprèss.
- **Public**: descobrís festivals, seguís corts e contacta amb la comunitat.

## Çò que pòdes far

- **Festivals e convocatòrias**: cada festivau pòt aver mantas convocatòrias dubèrtas amb sas règulas pròprias e formularis d'inscripcion.
- **Corts**: puja cortmetratges, liga-los a convocatòrias e a localizacions de rodatge.
- **Perfils amb palmarés**: palmarés ligat a festivals de la plataforma o extèrne mejançant ligams, amb contraròtle de privacitat camp per camp.
- **Chat**: messatges dirèctes e de grop o canau per festivau, amb chiframent d'extrèm a extrèm.
- **Mapas**: sèts e localizacions de rodatge en mapas interactius, amb dubertura dins ta app de mapas favorita.
- **Sens connexion**: l'app contunha de foncionar offline e sincroniza tos cambiaments en tornar trobar la connexion.
- **Dins ta lenga**: espanhòu, anglés, francés, alemand, italian, catalan, euskara, galician e occitan, amb deteccion automatica.

## Requesits e aviada

### Requesits minims

- Python 3.12+
- Flutter SDK >= 3.0.0 y < 4.0.0
- Git
- Docker y Docker Compose para despliegue/entorno productivo
- Navegador con soporte para web (recomendado Chrome/Brave)

### Aviada rapida

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

Aquò quilha lo backend en `http://localhost:8000` e l'app en mòde locau; l'API expausa Swagger/OpenAPI en `/docs`. Pòdes desactivar qual que siá de las doas partidas amb `--no-backend` o `--no-frontend`.

### Autras opcions utilas

```bash
start.bat --help
start.bat --migrate
start.bat --build
start.bat --build-all
```

Consulta la referéncia completa de l'aviada e desplegament en [docs/oc/HERRAMIENTAS.md](docs/oc/HERRAMIENTAS.md) e [docs/oc/USO.md](docs/oc/USO.md).

## Variablas d'environa e configuracion

### Backend

Crea o ajusta `backend/.env` amb almens:

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
```

Per environa productiva s'utiliza MariaDB; los scripts e la documentacion de desplegament o gerisson amb Docker.

### Frontend

L'app reutiliza lo backend per URL, normalament amb `--dart-define`:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

L'aviada automatica del projècte ja configura aquò quand s'utiliza `start.*`.

## Estat del projècte

🚧 **En desvolopament actiu** — Festivals, corts, chat amb E2EE, mapas, mòde offline e 9 lengas que foncionan; amb tèsts en backend (~1400) e frontend (69 fichièrs).

**Roadmap pròche:**

- [ ] Notificaciones push (Firebase/APNs)
- [ ] AppImage Linux firmado
- [ ] Windows MSI installer
- [x] Documentación API OpenAPI exportable (`/openapi.json` sin operationIds duplicados + `docs/oc/API.md` regenerado)

## Documentacion del projècte

Lo mapa de documentacion es en [docs/oc/README.md](docs/oc/README.md). Es la melhor intrada per cada tipe d'utilizaire:

- [docs/oc/USO.md](docs/oc/USO.md): aviada, operacion, environa e usatge vidant
- [docs/oc/ADMINISTRACION.md](docs/oc/ADMINISTRACION.md): administracion, comptes e desplegament
- [docs/oc/INFRAESTRUCTURA.md](docs/oc/INFRAESTRUCTURA.md): Docker, pòrts, CI e infra
- [docs/oc/SEGURIDAD.md](docs/oc/SEGURIDAD.md): tokens, politicas e checklist de produccion
- [docs/oc/ARQUITECTURA.md](docs/oc/ARQUITECTURA.md): arquitectura backend/frontend e fluxes claus
- [docs/oc/API.md](docs/oc/API.md): referéncia d'endpoints
- [docs/oc/DESARROLLO.md](docs/oc/DESARROLLO.md): cossí apondre endpoints o ecrans
- [docs/oc/BACKEND.md](docs/oc/BACKEND.md): guida del backend (capas, config, auth, tèsts)
- [docs/oc/DATABASE.md](docs/oc/DATABASE.md): esquèma e migracions

En mai, lo punt de partença per desvolopament e convencion de projècte es [AGENTS.md](AGENTS.md).

### Veire tanben

- [docs/oc/README.md](docs/oc/README.md): indici generau per audiéncia
- [docs/oc/HERRAMIENTAS.md](docs/oc/HERRAMIENTAS.md): comandas de build, tèst e aviada
- [docs/oc/FUNCIONAL.md](docs/oc/FUNCIONAL.md): usatge reau del produch per ròtle

### FAQ rapida

- **¿Necesito Docker para empezar?** No. El arranque local con `start.*` funciona sin Docker; Docker sirve para entorno productivo y builds reproducibles.
- **¿Qué hago si la API no responde?** Comprueba que el backend está corriendo en `http://localhost:8000` y que `/docs` responde.
- **¿Qué documento debo leer primero?** Si eres usuario, [docs/oc/USO.md](docs/oc/USO.md); si eres desarrollador, [docs/oc/ARQUITECTURA.md](docs/oc/ARQUITECTURA.md).
- **¿Cómo sé si un cambio requiere actualizar documentación?** Si cambia arranque, API, roles, permisos, variables de entorno o esquema, actualiza también la documentación que corresponda.

## Per desvolopaires

> Detalh complet en [`AGENTS.md`](AGENTS.md) (arquitectura, comandas e convencions) e en l'indici de [`docs/`](docs/oc/README.md) (guidas per ròtle: foncionau, usatge, administracion, infraestructura, seguretat, arquitectura, API).

**D'un uèlh**: backend FastAPI en capas (routers → servicis → modèls SQLAlchemy, SQLite en dev / MariaDB en prod, JWT + refresh, 18 migracions Alembic); frontend Flutter Material 3 amb dark mode (singletons + `setState()` + streams, Hive offline, 24 widgets reutilizables).

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

## Desvolopament locau

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

Backend + frontend (nginx) + MariaDB. Los builds distribuits (web, Windows, Linux, Android) se gerisson amb `start.bat --build-all` e lo jòc de scripts de [docs/oc/HERRAMIENTAS.md](docs/oc/HERRAMIENTAS.md).

## Solucion de problèmas

### Lo backend non avia

- Verifica que Python 3.12+ esté instalado.
- Comprueba que `backend/.env` existe y es válido.
- Ejecuta `cd backend && python -m uvicorn app.main:app --reload` para ver el error real.

### L'app non connecta amb l'API

- Asegúrate de que el backend está en `http://localhost:8000`.
- Revisa si `BACKEND_URL` se está pasando con `--dart-define`.
- Comprueba que la API responde en `/docs`.

### Problèmas amb bancas de donadas o migracions

- Usa `cd backend && alembic upgrade head`.
- Si cambias de SQLite a MariaDB, revisa [docs/oc/USO.md](docs/oc/USO.md) y [docs/oc/DATABASE.md](docs/oc/DATABASE.md).

### Frontend amb errors de Flutter

- Ejecuta `cd frontend && flutter pub get`.
- Si hay problemas de generación de código, sigue la documentación de Hive y build_runner en [docs/oc/ARQUITECTURA.md](docs/oc/ARQUITECTURA.md).

## Contribuir

1. Haz un fork del repositorio.
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`).
3. Haz commit con mensajes claros y descriptivos (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Empuja la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request con contexto, cambios y validación.

**Convencions de qualitat:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` e `flutter test` devon passar abans de fusionar.

## Licéncia

Aqueste projècte es jos la **Licéncia MIT**. Consulta [LICENSE](LICENSE).
