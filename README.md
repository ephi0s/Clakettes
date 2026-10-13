# Clakettes

La plataforma donde los festivales de cine viven todo el año: convocatorias, cortos, equipos, sedes y público en un mismo lugar.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

Funciona en web, Android, iOS y escritorio (Windows, macOS, Linux), en 9 idiomas y también sin conexión.

---

## ¿Para quién es?

- **Festivales**: publica tu festival, abre convocatorias, recibe cortos, organiza comités y jurados, gestiona sedes y comunica tu palmarés.
- **Profesionales del cine**: crea tu perfil (dirección, interpretación, sonido, guion, montaje, vestuario y más), muestra tu palmarés y conecta con festivales y equipos.
- **Equipos express**: coordina tu grupo de rodaje, geolocaliza a participantes y presenta tu corto a concursos express.
- **Público**: descubre festivales, sigue cortos y contacta con la comunidad.

## Qué puedes hacer

- **Festivales y convocatorias**: cada festival puede tener varias convocatorias abiertas con sus propias reglas y formularios de inscripción.
- **Cortos**: sube cortometrajes, vincúlalos a convocatorias y a localizaciones de rodaje.
- **Perfiles con palmarés**: palmarés vinculado a festivales de la plataforma o externo mediante enlaces, con control de privacidad campo por campo.
- **Chat**: mensajes directos y de grupo o canal por festival, con cifrado de extremo a extremo.
- **Mapas**: sedes y localizaciones de rodaje en mapas interactivos, con apertura en tu app de mapas favorita.
- **Sin conexión**: la app sigue funcionando offline y sincroniza tus cambios al recuperar la conexión.
- **En tu idioma**: español, inglés, francés, alemán, italiano, catalán, euskera, gallego y occitano, con detección automática.

## Requisitos y arranque

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

Esto levanta el backend en `http://localhost:8000` y la app en modo local; la API expone Swagger/OpenAPI en `/docs`. Puedes desactivar cualquiera de las dos partes con `--no-backend` o `--no-frontend`.

### Otras opciones útiles

```bash
start.bat --help
start.bat --migrate
start.bat --build
start.bat --build-all
```

Consulta la referencia completa del arranque y despliegue en [docs/HERRAMIENTAS.md](docs/HERRAMIENTAS.md) y [docs/USO.md](docs/USO.md).

## Variables de entorno y configuración

### Backend

Crea o ajusta `backend/.env` con al menos:

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
```

Para entorno productivo se usa MariaDB; los scripts y la documentación de despliegue lo gestionan con Docker.

### Frontend

La app reutiliza el backend por URL, normalmente con `--dart-define`:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

El arranque automático del proyecto ya configura esto cuando se usa `start.*`.

## Estado del proyecto

🚧 **En desarrollo activo** — Festivales, cortos, chat con E2EE, mapas, modo offline y 9 idiomas funcionando; con tests en backend (~1400) y frontend (69 archivos).

**Roadmap próximo:**

- [ ] Notificaciones push (Firebase/APNs)
- [ ] AppImage Linux firmado
- [ ] Windows MSI installer
- [x] Documentación API OpenAPI exportable (`/openapi.json` sin operationIds duplicados + `docs/API.md` regenerado)

## Documentación del proyecto

El mapa de documentación está en [docs/README.md](docs/README.md). Es la mejor entrada para cada tipo de usuario:

- [docs/USO.md](docs/USO.md): arranque, operación, entorno y uso diario
- [docs/ADMINISTRACION.md](docs/ADMINISTRACION.md): administración, cuentas y despliegue
- [docs/INFRAESTRUCTURA.md](docs/INFRAESTRUCTURA.md): Docker, puertos, CI y infra
- [docs/SEGURIDAD.md](docs/SEGURIDAD.md): tokens, políticas y checklist de producción
- [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md): arquitectura backend/frontend y flujos clave
- [docs/API.md](docs/API.md): referencia de endpoints
- [docs/DESARROLLO.md](docs/DESARROLLO.md): cómo añadir endpoints o pantallas
- [docs/BACKEND.md](docs/BACKEND.md): guía del backend (capas, config, auth, tests)
- [docs/DATABASE.md](docs/DATABASE.md): esquema y migraciones

Además, el punto de partida para desarrollo y convención de proyecto es [AGENTS.md](AGENTS.md).

### Ver también

- [docs/README.md](docs/README.md): índice general por audiencia
- [docs/HERRAMIENTAS.md](docs/HERRAMIENTAS.md): comandos de build, test y arranque
- [docs/FUNCIONAL.md](docs/FUNCIONAL.md): uso real del producto por rol

### FAQ rápida

- **¿Necesito Docker para empezar?** No. El arranque local con `start.*` funciona sin Docker; Docker sirve para entorno productivo y builds reproducibles.
- **¿Qué hago si la API no responde?** Comprueba que el backend está corriendo en `http://localhost:8000` y que `/docs` responde.
- **¿Qué documento debo leer primero?** Si eres usuario, [docs/USO.md](docs/USO.md); si eres desarrollador, [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md).
- **¿Cómo sé si un cambio requiere actualizar documentación?** Si cambia arranque, API, roles, permisos, variables de entorno o esquema, actualiza también la documentación que corresponda.

## Para desarrolladores

> Detalle completo en [`AGENTS.md`](AGENTS.md) (arquitectura, comandos y convenciones) y en el índice de [`docs/`](docs/README.md) (guías por rol: funcional, uso, administración, infraestructura, seguridad, arquitectura, API).

**De un vistazo**: backend FastAPI en capas (routers → servicios → modelos SQLAlchemy, SQLite en dev / MariaDB en prod, JWT + refresh, 18 migraciones Alembic); frontend Flutter Material 3 con dark mode (singletons + `setState()` + streams, Hive offline, 24 widgets reutilizables).

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

## Desarrollo local

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
flutter run
```

## Despliegue

```bash
docker compose --profile prod up -d
```

Backend + frontend (nginx) + MariaDB. Los builds distribuidos (web, Windows, Linux, Android) se gestionan con `start.bat --build-all` y el conjunto de scripts de [docs/HERRAMIENTAS.md](docs/HERRAMIENTAS.md).

## Solución de problemas

### El backend no arranca

- Verifica que Python 3.12+ esté instalado.
- Comprueba que `backend/.env` existe y es válido.
- Ejecuta `cd backend && python -m uvicorn app.main:app --reload` para ver el error real.

### La app no conecta con la API

- Asegúrate de que el backend está en `http://localhost:8000`.
- Revisa si `BACKEND_URL` se está pasando con `--dart-define`.
- Comprueba que la API responde en `/docs`.

### Problemas con bases de datos o migraciones

- Usa `cd backend && alembic upgrade head`.
- Si cambias de SQLite a MariaDB, revisa [docs/USO.md](docs/USO.md) y [docs/DATABASE.md](docs/DATABASE.md).

### Frontend con errores de Flutter

- Ejecuta `cd frontend && flutter pub get`.
- Si hay problemas de generación de código, sigue la documentación de Hive y build_runner en [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md).

## Contribuir

1. Haz un fork del repositorio.
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`).
3. Haz commit con mensajes claros y descriptivos (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Empuja la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request con contexto, cambios y validación.

**Convenciones de calidad:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` y `flutter test` deben pasar antes de fusionar.

## Licencia

Este proyecto está bajo la **Licencia MIT**. Consulta [LICENSE](LICENSE).
