# Clakettes

A plataforma onde os festivais de cine viven todo o ano: convocatorias, curtas, equipos, sedes e público nun mesmo lugar.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

Funciona en web, Android, iOS e escritorio (Windows, macOS, Linux), en 9 idiomas e tamén sen conexión.

---

## Para quen é?

- **Festivais**: publica o teu festival, abre convocatorias, recibe curtas, organiza comités e xurados, xestiona sedes e comunica o teu palmarés.
- **Profesionais do cine**: crea o teu perfil (dirección, interpretación, son, guión, montaxe, vestiario e máis), mostra o teu palmarés e conecta con festivais e equipos.
- **Equipos express**: coordina o teu grupo de rodaxe, xeolocaliza a participantes e presenta a túa curta a concursos express.
- **Público**: descobre festivais, segue curtas e contacta coa comunidade.

## Que podes facer

- **Festivais e convocatorias**: cada festival pode ter varias convocatorias abertas coas súas propias regras e formularios de inscrición.
- **Curtas**: sube curtametraxes, vincúlaas a convocatorias e a localizacións de rodaxe.
- **Perfís con palmarés**: palmarés vinculado a festivais da plataforma ou externo mediante ligazóns, con control de privacidade campo por campo.
- **Chat**: mensaxes directas e de grupo ou canal por festival, con cifrado de extremo a extremo.
- **Mapas**: sedes e localizacións de rodaxe en mapas interactivos, con apertura na túa app de mapas favorita.
- **Sen conexión**: a app segue funcionando offline e sincroniza os teus cambios ao recuperar a conexión.
- **No teu idioma**: español, inglés, francés, alemán, italiano, catalán, éuscaro, galego e occitano, con detección automática.

## Requisitos e arranque

### Requisitos mínimos

- Python 3.12+
- Flutter SDK >= 3.0.0 y < 4.0.0
- Git
- Docker y Docker Compose para despliegue/entorno productivo
- Navegador con soporte para web (recomendado Chrome/Brave)

### Inicio rápido

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

Isto levanta o backend en `http://localhost:8000` e a app en modo local; a API expón Swagger/OpenAPI en `/docs`. Podes desactivar calquera das dúas partes con `--no-backend` ou `--no-frontend`.

### Outras opcións útiles

```bash
start.bat --help
start.bat --migrate
start.bat --build
start.bat --build-all
```

Consulta a referencia completa do arranque e despregamento en [docs/HERRAMIENTAS.md](docs/HERRAMIENTAS.gl.md) e [docs/USO.md](docs/USO.gl.md).

## Variables de entorno e configuración

### Backend

Crea ou axusta `backend/.env` con polo menos:

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
```

Para entorno produtivo úsase MariaDB; os scripts e a documentación de despregamento xestiónano con Docker.

### Frontend

A app reutiliza o backend por URL, normalmente con `--dart-define`:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

O arranque automático do proxecto xa configura isto cando se usa `start.*`.

## Estado do proxecto

🚧 **En desenvolvemento activo** — Festivais, curtas, chat con E2EE, mapas, modo offline e 9 idiomas funcionando; con tests en backend (~1400) e frontend (69 arquivos).

**Roadmap próximo:**

- [ ] Notificaciones push (Firebase/APNs)
- [ ] AppImage Linux firmado
- [ ] Windows MSI installer
- [x] Documentación API OpenAPI exportable (`/openapi.json` sin operationIds duplicados + `docs/API.md` regenerado)

## Documentación do proxecto

O mapa de documentación está en [docs/README.md](docs/README.gl.md). É a mellor entrada para cada tipo de usuario:

- [docs/USO.md](docs/USO.gl.md): arranque, operación, entorno e uso diario
- [docs/ADMINISTRACION.md](docs/ADMINISTRACION.gl.md): administración, contas e despregamento
- [docs/INFRAESTRUCTURA.md](docs/INFRAESTRUCTURA.gl.md): Docker, portos, CI e infra
- [docs/SEGURIDAD.md](docs/SEGURIDAD.gl.md): tokens, políticas e checklist de produción
- [docs/ARQUITECTURA.md](docs/ARQUITECTURA.gl.md): arquitectura backend/frontend e fluxos clave
- [docs/API.md](docs/API.gl.md): referencia de endpoints
- [docs/DESARROLLO.md](docs/DESARROLLO.gl.md): como engadir endpoints ou pantallas
- [docs/BACKEND.md](docs/BACKEND.gl.md): guía do backend (capas, config, auth, tests)
- [docs/DATABASE.md](docs/DATABASE.gl.md): esquema e migracións

Ademais, o punto de partida para desenvolvemento e convención de proxecto é [AGENTS.md](AGENTS.md).

### Ver tamén

- [docs/README.md](docs/README.gl.md): índice xeral por audiencia
- [docs/HERRAMIENTAS.md](docs/HERRAMIENTAS.gl.md): comandos de build, test e arranque
- [docs/FUNCIONAL.md](docs/FUNCIONAL.gl.md): uso real do produto por rol

### FAQ rápida

- **Necesito Docker para empezar?** Non. O arranque local con `start.*` funciona sen Docker; Docker serve para entorno produtivo e builds reproducibles.
- **Que fago se a API non responde?** Comproba que o backend está correndo en `http://localhost:8000` e que `/docs` responde.
- **Que documento debo ler primeiro?** Se es usuario, [docs/USO.md](docs/USO.gl.md); se es desenvolvedor, [docs/ARQUITECTURA.md](docs/ARQUITECTURA.gl.md).
- **Como sei se un cambio require actualizar documentación?** Se cambia arranque, API, roles, permisos, variables de entorno ou esquema, actualiza tamén a documentación que corresponda.

## Para desenvolvedores

> Detalle completo en [`AGENTS.md`](AGENTS.md) (arquitectura, comandos e convencións) e no índice de [`docs/`](docs/README.gl.md) (guías por rol: funcional, uso, administración, infraestrutura, seguridade, arquitectura, API).

**Dunha ollada**: backend FastAPI en capas (routers → servizos → modelos SQLAlchemy, SQLite en dev / MariaDB en prod, JWT + refresh, 18 migracións Alembic); frontend Flutter Material 3 con dark mode (singletons + `setState()` + streams, Hive offline, 24 widgets reutilizables).

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

## Desenvolvemento local

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
flutter run
```

## Despregamento

```bash
docker compose --profile prod up -d
```

Backend + frontend (nginx) + MariaDB. Os builds distribuídos (web, Windows, Linux, Android) xestiónanse con `start.bat --build-all` e o conxunto de scripts de [docs/HERRAMIENTAS.md](docs/HERRAMIENTAS.gl.md).

## Solución de problemas

### O backend non arranca

- Verifica que Python 3.12+ estea instalado.
- Comproba que `backend/.env` existe e é válido.
- Executa `cd backend && python -m uvicorn app.main:app --reload` para ver o erro real.

### A app non conecta coa API

- Asegúrate de que o backend está en `http://localhost:8000`.
- Revisa se `BACKEND_URL` se está pasando con `--dart-define`.
- Comproba que a API responde en `/docs`.

### Problemas con bases de datos ou migracións

- Usa `cd backend && alembic upgrade head`.
- Se cambias de SQLite a MariaDB, revisa [docs/USO.md](docs/USO.gl.md) e [docs/DATABASE.md](docs/DATABASE.gl.md).

### Frontend con erros de Flutter

- Executa `cd frontend && flutter pub get`.
- Se hai problemas de xeración de código, segue a documentación de Hive e build_runner en [docs/ARQUITECTURA.md](docs/ARQUITECTURA.gl.md).

## Contribuír

1. Fai un fork do repositorio.
2. Crea unha rama (`git checkout -b feature/nueva-funcionalidad`).
3. Fai commit con mensaxes claras e descritivas (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Empuxa a rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request con contexto, cambios e validación.

**Convencións de calidade:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` e `flutter test` deben pasar antes de fusionar.

## Licenza

Este proxecto está baixo a **Licenza MIT**. Consulta [LICENSE](LICENSE).
