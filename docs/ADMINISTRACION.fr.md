# Administration — Clakettes

Guide pour qui exploite un déploiement. Infrastructure dans [INFRAESTRUCTURA.fr.md](INFRAESTRUCTURA.fr.md), liste de contrôle de production dans [SEGURIDAD.fr.md](SEGURIDAD.fr.md).

## Compte initial

En non-prod (`APP_ENV != production`) le démarrage crée `admin` / `setup` (`admin@clakettes.com`, rôle admin) s'il n'existe pas ; en prod **il n'est pas créé**. Changez le mot de passe en entrant. La création utilise `POST /api/users/login` (JWT 30 min + refresh 30 j, liste et révoque les sessions sur `/api/auth/sessions`).

## Endpoints `/api/admin` (rôle admin uniquement, 403 sinon)

| Método y ruta | Efecto |
|---|---|
| `GET /api/admin/stats` | Contadores: usuarios, festivales, cortos, mensajes, activos |
| `GET /api/admin/tables` | Tablas (menos `alembic_version`) con nº de filas |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 si `confirm` no es `yes`, 403 si la contraseña no verifica; rate-limit propio 3/300s (429, bypass con `TESTING=true`) |

## Secrets et rotation

- `SECRET_KEY` : obligatoire en prod (le démarrage échoue avec celle d'exemple et indique `secrets.token_urlsafe(64)`). La changer invalide tous les JWT et refresh tokens : faites-le en fenêtre de maintenance et prévenez (tous refont login).
- `CORS_ORIGINS` : origines explicites en prod ; `*` + credentials est interdit et bloque le démarrage.
- Derrière proxy : `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontal.

## Sauvegardes et migrations

- SQLite : copier `*.db` à chaud arrêté (`-Kill` avant). MariaDB : `mariadb-dump` (volume `db-data`).
- Migrations : `alembic upgrade head` depuis `backend/` (18 versions ; prod **uniquement** Alembic, jamais `create_all`).
- Changement de moteur : `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev) ; détail dans [DATABASE.fr.md](DATABASE.fr.md).

## Dépannage

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

## Voir aussi

- [USO.fr.md](USO.fr.md) : démarrage et exploitation du système
- [INFRAESTRUCTURA.fr.md](INFRAESTRUCTURA.fr.md) : déploiement, ports et CI
- [SEGURIDAD.fr.md](SEGURIDAD.fr.md) : liste de contrôle de durcissement et politiques
- [../README.fr.md](../README.fr.md) : contexte global du projet
