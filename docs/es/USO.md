# Uso — Clakettes

[ES](USO.md) · [EN](../en/USO.md) · [FR](../fr/USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Arranque rápido

| Quiero | Comando |
|---|---|
| Todo en local | `.\start.ps1` o `./start.sh` (Docker si hay, local si no) |
| Solo backend / frontend | `-NoFrontend` / `-NoBackend` |
| Probar en navegador de desarrollo | default / `-Dev` (o `-Web` para forzar modo local) |
| Producción local | `-Final` (build web + serve) |
| Tests | `-TestBackend` / `-TestFrontend` |
| Migraciones / con MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Parar todo | `-Kill` |
| Instalar dependencias que falten | `-InstallMissing` (Windows: winget + git clone; Linux/macOS: gestor del SO + git clone) |
| Revisar el entorno sin arrancar | `-Check` (doctor: Docker, Python, Flutter, .venv, puertos; sale 1 si falta algo) |
| Builds distribuibles | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Sin Docker, el lanzador crea un entorno bare-metal local: detecta Python 3.12+ y Flutter, muestra cómo instalarlos según tu SO y ofrece instalarlos con `-InstallMissing` (pregunta antes salvo que vayas con el flag).

URLs dev: backend `http://localhost:8000` (Swagger en `/docs`), frontend `http://localhost:3000`.
Si el puerto está ocupado se reasigna solo (mira `[PUERTO]` en la salida).
Admin inicial (solo no-prod): `admin` / `setup` — cambiar al entrar.

## Configuración

| Variable / flag | Dónde | Efecto |
|---|---|---|
| `BACKEND_URL` | `--dart-define` o pantalla de backend en la app | URL del API (persiste en SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev; en Docker `./data/clakettes.db`) o `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obligatorio) |
| `SECRET_KEY` | env (obligatoria en `APP_ENV=production`) | Firma JWT; default inseguro bloquea el arranque en prod |
| `CORS_ORIGINS` | env | Orígenes explícitos en prod (`*` prohibido con credenciales) |
| `APP_ENV` | env | `development` crea admin + `create_all`; `production` exige Alembic |
| `PUBLIC_BASE_URL` | `backend/.env` | Dominio público del nodo; aparece en el manifiesto y en los bundles de portabilidad |
| `MTLS_REQUIRED` | env | Obliga a peer mTLS verificado en federación (CN y PEM del certificado) |
| `MTLS_CA_BUNDLE_PATH` | env | CA raíz para validar certificados de clientes federados |
| `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | env | PEM del certificado y clave privada que firman el manifiesto (RSA-SHA256) |
| `TESTING`, `SKIP_AUTO_MIGRATE` | env | `1/true/yes/on`: `TESTING` desactiva rate limits y auto-migración; `SKIP_AUTO_MIGRATE` omite solo la auto-migración |
| `RATE_LIMITS_DB_PATH` | env | Ruta de la BD SQLite de límites (default `backend/rate_limits.db`) |
| `JWT_ISSUER`, `JWT_AUDIENCE`, `ACCESS_TOKEN_EXPIRE_MINUTES` | env | Claims y TTL del access JWT |
| `PAYMENTS_PROVIDER`, `MOCK_WEBHOOK_SECRET`, `MOCK_PAYMENTS_FORCE_FAIL` | env | Pasarela (`mock` por defecto) y secretos del webhook simulado |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `REDSYS_*` | env | Credenciales de pago reales; detalle en [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) |

**Nota de pagos**: `PAYMENTS_PROVIDER=mock` es el valor por defecto (`backend/app/config.py`). Stripe y Redsys NO están operativos hasta cablear sus webhooks (`POST /api/payments/webhook/{stripe,redsys}`); hoy solo funciona el simulado. El `confirm` de Redsys devuelve siempre `"pending"`.

## Operación

- **Migrar**: `alembic upgrade head` desde `backend/` (Docker: `-Migrate`).
- **Migración automática**: la app migra sola la DB al arrancar y sella las DB nuevas con la revisión actual; `SKIP_AUTO_MIGRATE=1` para omitirlo (DBs gestionadas externamente).
- **SQLite → MariaDB**: `export_sqlite_to_mariadb.py`; vuelta con `import_mariadb_to_sqlite.py` (detalle en [DATABASE.md](DATABASE.md)).
- **Backups**: SQLite = copiar `*.db`; MariaDB = `mariadb-dump` (volumen `db-data` en Docker).
- **Logs**: uvicorn stdout (tokens DAV ya redactados); errores de API en SnackBar + `debugPrint`.
- **Límites**: cuerpos ≤10 MB (413 si mayor); rate limit con 429 + reintento (global 100/60 s por IP, `/dav` 600/60 s, login 5/300 s, refresh 20/60 s, reset 3/300 s, federación 60/60 s; chat 10/60 s por nodo y usuario). `TESTING` ∈ {1,true,yes,on} desactiva todos los límites.
- **Sin conexión**: la caché Hive guarda la procedencia de cada nodo; `reconcile` fusiona al reconectar y `clearOrigin` descarta un nodo. Si algunos nodos no responden pero el principal sí, aparece `DegradedNodesBanner` con el recuento y un botón para recargar.
- **Medios**: las rutas `/uploads/...` que devuelve la API se anteponen al servidor activo en el cliente (`resolveMediaUrl()`); las URLs `http(s)` se usan tal cual.
- **Federación**: comprueba un nodo tercero con `python tools/federation_conformance.py <url> [--json]`; la salud del peering está en `/api/federation/resilience/health` y las métricas p50/p95 en `/metrics`.
- **Portabilidad**: exporta/importa bundles desde `/api/federation/portability/{bundles,imports}` y consulta las redirecciones de identidad en `/redirects/{ref}`.

## Roles de usuario

`admin` (todo) → `organizer` (su festival: eventos, formularios, comités) → `attendee`/`juror`/etc. (asignados por organizers; el auto-join solo da `attendee`). Canales: `admin`/`moderator`/`member`; comités con conteo de miembros en lista.

## Funciones en desarrollo activo

🚧 Las siguientes funciones están en desarrollo activo y pueden cambiar:

- **Perfiles sociales**: muros de publicaciones (microblogging con Markdown e incrustados de vídeo y podcast) en perfiles de usuario y festival, con hilos de respuestas opcionales por publicación y moderación por roles (administradores, gestión del festival, moderadores). Sin reacciones, stickers ni GIF por ahora.
- **Personalización de perfiles**: portada, tagline y enlaces sociales en usuarios y festivales.
- **Insignias**: desactivadas por defecto; solo el equipo administrativo puede activarlas (`PUT /api/badges/settings`). Las insignias de plataforma las otorgan los administradores; las de mérito de festival (veterano, popular, rol, premio especial), su gestión. Cada insignia lleva una imagen (SVG preferido).
- **Votación del jurado**: ya operativa (puntuación por obra, agregación y anonimato opcional); solo admite cortos del festival asignado.

## Ver también

- [README.md](../../README.md): descripcion general del proyecto y acceso rápido
- [HERRAMIENTAS.md](HERRAMIENTAS.md): scripts y comandos de ejecucion
- [ADMINISTRACION.md](ADMINISTRACION.md): administración del despliegue y rotacion de secretos
- [SEGURIDAD.md](SEGURIDAD.md): checklist y buenas practicas de produccion