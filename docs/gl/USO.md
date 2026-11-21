# Uso — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](USO.md) · [OC](../oc/USO.md)

## Arranque rápido

| Quero | Comando |
|---|---|
| Todo en local | `.\start.ps1` ou `./start.sh` (Docker se hai, local se non) |
| Só backend / frontend | `-NoFrontend` / `-NoBackend` |
| Probar en navegador | `-Web` (modo local) |
| Produción local | `-Final` (build web + serve) |
| Tests | `-TestBackend` / `-TestFrontend` |
| Migracións / con MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Parar todo | `-Kill` |
| Instalar dependencias que falten | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: xestor do SO + git clone) |
| Revisar o contorno sen arrancar | `-Check` (doctor: Docker, Python, Flutter, .venv, portos; sae 1 se falta algo) |
| Builds distribuíbles | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Sen Docker, o lanzador crea un contorno bare-metal local: detecta Python 3.12+ e Flutter, mostra como instalalos segundo o teu SO e ofrece instalalos con `-InstallMissing` (pregunta antes salvo que vaias co flag).

URLs dev: backend `http://localhost:8000` (Swagger en `/docs`), frontend `http://localhost:3000`.
Se o porto está ocupado reasígnase só (mira `[PUERTO]` na saída).
Admin inicial (só non-prod): `admin` / `setup` — cambiar ao entrar.

## Configuración

| Variable / flag | Onde | Efecto |
|---|---|---|
| `BACKEND_URL` | `--dart-define` ou pantalla de backend na app | URL da API (persiste en SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; en Docker `./data/clakettes.db`) ou `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obrigatorio) |
| `SECRET_KEY` | env (obrigatoria en `APP_ENV=production`) | Sinatura JWT; default inseguro bloquea o arranque en prod |
| `CORS_ORIGINS` | env | Orixes explícitos en prod (`*` prohibido con credenciais) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` esixe Alembic |
| `PUBLIC_BASE_URL` | `backend/.env` | Dominio público do nodo; aparece no manifesto e nos bundles de portabilidade |
| `MTLS_REQUIRED` | env | Obliga a peer mTLS verificado en federación (CN e PEM do certificado) |
| `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | env | PEM do certificado e clave privada que asinan o manifesto (RSA-SHA256) |

## Operación

- **Migrar**: `alembic upgrade head` desde `backend/` (Docker: `-Migrate`).
- **Migración automática**: a app migra soa a DB ao arrancar e sela as DB novas coa revisión actual; `SKIP_AUTO_MIGRATE=1` para omitilo (DB xestionadas externamente).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; volta con `import_mariadb_to_sqlite.py` (detalle en [DATABASE.md](DATABASE.md)).
- **Backups**: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` (volume `db-data` en Docker).
- **Logs**: stdout de uvicorn (tokens DAV xa redactados); erros de API en SnackBar + `debugPrint`.
- **Límites**: corpos ≤10 MB (413 se maior); rate limit con 429 + reintento (federación 60/60 s por IP; chat 10/60 s por nodo e usuario, desactivado con `TESTING=true`).
- **Federación**: comproba un nodo terceiro con `python tools/federation_conformance.py <url> [--json]`; a saúde do peering está en `/api/federation/resilience/health` e as métricas p50/p95 en `/metrics`.
- **Portabilidade**: exporta/importa bundles desde `/api/federation/portability/{bundles,imports}` e consulta as redireccións de identidade en `/redirects/{ref}`.

## Roles de usuario

`admin` (todo) → `organizer` (o seu festival: eventos, formularios, comités) → `attendee`/`juror`/etc. (asignados polos organizers; o auto-join só dá `attendee`). Canais: `admin`/`moderator`/`member`; comités con conteo de membros na lista.

## Funcións en desenvolvemento activo

🚧 As seguintes funcións están en desenvolvemento activo e poden cambiar:

- **Perfis sociais**: muros de publicacións (microblogging con Markdown e incrustacións de vídeo e podcast) en perfís de usuario e festival, con fíos de respostas opcionais por publicación e moderación por roles (administradores, xestión do festival, moderadores). Sen reaccións, pegatinas nin GIF por agora.
- **Personalización de perfís**: portada, tagline e ligazóns sociais en usuarios e festivais.
- **Insignias**: desactivadas por defecto; só o equipo administrativo pode activalas (`PUT /api/badges/settings`). As insignias de plataforma outorgánas os administradores; as de mérito de festival (veterano, popular, rol, premio especial), a súa xestión. Cada insignia leva unha imaxe (SVG preferido).
- **Votación do xurado**: puntuación por obra, agregación e anonimato opcional (fase 5 do roadmap).

## Ver tamén

- [README.gl.md](../../README.gl.md): descrición xeral do proxecto e acceso rápido
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts e comandos de execución
- [ADMINISTRACION.md](ADMINISTRACION.md): administración do despregue e rotación de segredos
- [SEGURIDAD.md](SEGURIDAD.md): checklist e boas prácticas de produción
