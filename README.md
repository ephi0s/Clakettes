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

## Empieza en 1 minuto

```bat
start.bat --dev
```

Eso arranca el backend (`http://localhost:8000`, con documentación en `/docs`) y la app. Sin backend: `start.bat --no-frontend` o `--no-backend`. Ver todas las opciones con `start.bat --help` (en PowerShell: `start.ps1`, en Linux/macOS: `start.sh`).

Necesitas tener instalados **Python 3.12+** y el **SDK de Flutter**; los scripts crean el entorno y descargan dependencias solos. Para producción hay `docker compose --profile prod up -d` (ver [Despliegue](#despliegue)).

## Estado del proyecto

🚧 **En desarrollo activo** — Festivales, cortos, chat con E2EE, mapas, modo offline y 9 idiomas funcionando; con tests en backend (~1320) y frontend (70 archivos).

**Roadmap próximo:**
- [ ] Notificaciones push (Firebase/APNs)
- [ ] AppImage Linux firmado
- [ ] Windows MSI installer
- [ ] Documentación API OpenAPI exportable

## Para desarrolladores

> Detalle completo en [`AGENTS.md`](AGENTS.md) (arquitectura, comandos y convenciones) y en el índice de [`docs/`](docs/README.md) (guías por rol: funcional, uso, administración, infraestructura, seguridad, arquitectura, API).

**De un vistazo**: backend FastAPI en capas (routers → servicios → modelos SQLAlchemy, SQLite en dev / MariaDB en prod, JWT + refresh, 15 migraciones Alembic); frontend Flutter Material 3 con dark mode (singletons + `setState()` + streams, Hive offline, 24 widgets reutilizables).

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

Configuración en `backend/.env` (`DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, puertos); la app toma el backend de `--dart-define=BACKEND_URL=...`.

### Despliegue

```bash
docker compose --profile prod up -d
```

Backend + frontend (nginx) + MariaDB. Builds distribubles (web, Windows, Linux, Android) con `start.bat --build-all`.

## Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'feat: añade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

**Convenciones:** [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`); `ruff check .` / `flutter analyze` y `pytest` / `flutter test` deben pasar.

## Licencia

Este proyecto está bajo la **Licencia MIT**. Consulta [LICENSE](LICENSE).
