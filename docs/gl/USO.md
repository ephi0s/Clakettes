# Uso — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](USO.md) · [OC](../oc/USO.md)

## Arranque rápido

| Queño | Comando |
|-------|---------|
| Todo en local | `.\start.ps1` ou `./start.sh` (Docker se hai, local se non) |
| Só backend / frontend | `-NoFrontend` / `-NoBackend` |
| Probar no navegador | `-Web` (modo local) |
| Produción local | `-Final` (build web + serve) |
| Testes | `-TestBackend` / `-TestFrontend` |
| Migracións / con MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Parar todo | `-Kill` |
| Instalar dependencias que faltan | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: xestor do SO + git clone) |
| Revisar o entorno sen arrancar | `-Check` (doctor: Docker, Python, Flutter, .venv, portos; sale 1 se falta algo) |
| Builds distribuíbles | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Sen Docker, o lanzador crea un entorno bare-metal local: detecta Python 3.12+ e Flutter, amosa como instalalos segundo o teu SO e ofrece instalalos con `-InstallMissing` (pregunta antes salvo que vayas co flag).

URLs dev: backend `http://localhost:8000` (Swagger en `/docs`), frontend `http://localhost:3000`.
Se o porto está ocupado reasígnase so (mira `[PUERTO]` na saída).
Admin inicial (só no-prod): `admin` / `setup` — cambiar ao entrar.

## Configuración

| Variable / flag | Onde | Efecto |
|-----------------|------|--------|
| `BACKEND_URL` | `--dart-define` ou pantalla de backend na app | URL da API (persiste en SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; en Docker `./data/clakettes.db`) ou `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obrigatorio) |
| `SECRET_KEY` | env (obrigatoria en `APP_ENV=production`) | Firma JWT; default inseguro bloquea o arranque en prod |
| `CORS_ORIGINS` | env | Oríxenes explícitas en prod (`*` prohibitido con credenciais) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` exige Alembic |

## Operación

- **Migración**: `alembic upgrade head` desde `backend/` (Docker: `-Migrate`).
- **Migración automática**: a app migra soa a DB ao arrancar e sella as DB novas co revisión actual; `SKIP_AUTO_MIGRATE=1` para omitilo (DBs xeestionadas externamente).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; volta con `import_mariadb_to_sqlite.py` (detalle en [DATABASE.md](DATABASE.md)).
- **Copias de seguridade**: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` (volume `db-data` en Docker).
- **Logs**: stdout de uvicorn (tokens DAV xa redactados); erros da API en SnackBar + `debugPrint`.
- **Límites**: corpos ≤10 MB (413 se maior); rate limit con 429 + reintento.

## Roles de usuario

`admin` (todo) → `organizer` (o seu festival: eventos, formulares, comités) → `attendee`/`juror`/etc. (asignados polos organizers; o auto-join só da `attendee`). Canles: `admin`/`moderator`/`member`; comités con contario de membros na lista.

## Funcións en desenvolvemento activo

🚧 As seguintes funcións están en desenvolvemento activo e poden cambiar:

- **Perfis sociais**: muros de publicacións (microblogging con Markdown e incrustados de vídeo e podcast) en perfís de usuario e festival, con hilos de resposta opcionales por publicación e moderación por roles (administradores, xestión do festival, moderadores). Sen reaccións, stickers nin GIF por ahora.
- **Personalización de perfis**: portada, tagline e enllaces sociais en usuarios e festivais.
- **Insignias**: desactivadas por defecto; só o equipo administrativo pode activalas (`PUT /api/badges/settings`). As insignias da plataforma otorganse polos administradores; as de mérito de festival (veterano, popular, rol, premio especial), a súa xestión. Cada insignia leva unha imaxe (SVG preferido).
- **Votaxe do xurado**: puntuación por obra, agregación e anonimato opcional (fase 5 do roadmap).

## Ver tamén

- [README.md](../../README.gl.md): descrición xeral do proxecto e acceso rápido
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts e comandos de execución
- [ADMINISTRACION.md](ADMINISTRACION.md): administración do despliegue e rotación de secretos
- [SEGURIDAD.md](SEGURIDAD.md): checklist e boas prácticas de produción