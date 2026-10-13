# Administration — Clakettes

Anleitung für alle, die ein Deployment betreiben. Infrastruktur in [INFRAESTRUCTURA.de.md](INFRAESTRUCTURA.de.md), Produktions-Checkliste in [SEGURIDAD.de.md](SEGURIDAD.de.md).

## Initiales Konto

In Nicht-Prod (`APP_ENV != production`) legt der Start `admin` / `setup` (`admin@clakettes.com`, Rolle admin) an, falls es nicht existiert; in Prod wird es **nicht erstellt**. Passwort nach dem Login ändern. Die Anmeldung nutzt `POST /api/users/login` (JWT 30 Min + Refresh 30 T, Sitzungen listen und widerrufen unter `/api/auth/sessions`).

## Endpunkte `/api/admin` (nur Rolle admin, sonst 403)

| Método y ruta | Efecto |
|---|---|
| `GET /api/admin/stats` | Contadores: usuarios, festivales, cortos, mensajes, activos |
| `GET /api/admin/tables` | Tablas (menos `alembic_version`) con nº de filas |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 si `confirm` no es `yes`, 403 si la contraseña no verifica; rate-limit propio 3/300s (429, bypass con `TESTING=true`) |

## Geheimnisse und Rotation

- `SECRET_KEY`: in Prod Pflicht (der Start schlägt mit dem Beispiel-Key fehl und weist auf `secrets.token_urlsafe(64)` hin). Rotation macht alle JWT- und Refresh-Tokens ungültig: in einem Wartungsfenster durchführen und ankündigen (alle müssen sich neu anmelden).
- `CORS_ORIGINS`: in Prod explizite Origins; `*` + Credentials ist verboten und blockiert den Start.
- Hinter einem Proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + Front-TLS.

## Backups und Migrationen

- SQLite: `*.db` bei gestopptem Dienst kopieren (`-Kill` vorher). MariaDB: `mariadb-dump` (Volume `db-data`).
- Migrationen: `alembic upgrade head` aus `backend/` (18 Versionen; Prod **nur** Alembic, niemals `create_all`).
- Engine-Wechsel: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); Details in [DATABASE.de.md](DATABASE.de.md).

## Fehlerbehebung

| Síntoma | Causa probable | Acción |
|---|---|---|
| Arranque aborta por `SECRET_KEY` / CORS | default inseguro o `*` en prod | Define `SECRET_KEY` y `CORS_ORIGINS` explícitos |
| `401` en endpoints públicos de formularios | enlace mal generado | Revisa el token del link; el acceso anónimo no da 401 por sí solo |
| `403` gestionando festival/canal/comité | caller sin rol | Verifica membresía y rol (`GET …/members`); el auto-join solo da `attendee` |
| `409` al unirse | ya es miembro | Usa `leave` o gestiona desde miembros |
| `413` subiendo | supera 10 MB cuerpo / 5 MB imagen / 100 MB vídeo / 10 MB pdf | Comprime o parte el archivo |
| `429` generalizado | rate limit 100/60s por IP (o 3/300s en reset) | Espera y reintenta; revisa `TESTING=true` residual |
| WS no conecta | JWT sin `type=access` o sesión revocada/expirada | Re-login; revisa `/api/auth/sessions` |
| App offline no sincroniza | cola con fallos agotados (`failed`, 3 intentos + backoff) | Revisa errores en el prompt de sync; `clear()` tras confirmar en logout |

## Siehe auch

- [USO.de.md](USO.de.md): Start und Betrieb des Systems
- [INFRAESTRUCTURA.de.md](INFRAESTRUCTURA.de.md): Deployment, Ports und CI
- [SEGURIDAD.de.md](SEGURIDAD.de.md): Härtungs-Checkliste und Richtlinien
- [../README.de.md](../README.de.md): globaler Projektkontext
