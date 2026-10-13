# Administrazioa — Clakettes

Hedapen bat operatzen duenari zuzendutako gida. Azpiegitura [INFRAESTRUCTURA.md](INFRAESTRUCTURA.eu.md)-n, ekoizpeneko checklist-a [SEGURIDAD.md](SEGURIDAD.eu.md)-n.

## Hasierako kontua

Ez-prod ingurunean (`APP_ENV != production`) abiaraztean `admin` / `setup` (`admin@clakettes.com`, admin rolarekin) sortzen da existitzen ez bada; prod-ean **ez da sortzen**. Aldatu pasahitza sartzean. Alta egiteko `POST /api/users/login` erabiltzen da (JWT 30 min + refresh 30 egun, saioak zerrendatu eta ezeztatu `/api/auth/sessions`-en).

## `/api/admin` endpoint-ak (admin rola soilik, bestela 403)

| Método y ruta | Efecto |
|---|---|
| `GET /api/admin/stats` | Contadores: usuarios, festivales, cortos, mensajes, activos |
| `GET /api/admin/tables` | Tablas (menos `alembic_version`) con nº de filas |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 si `confirm` no es `yes`, 403 si la contraseña no verifica; rate-limit propio 3/300s (429, bypass con `TESTING=true`) |

## Sekretuak eta errotazioa

- `SECRET_KEY`: nahitaezkoa prod-ean (abiarazteak huts egiten du adibidekoarekin eta `secrets.token_urlsafe(64)` adierazten du). Errotatzeak JWT eta refresh token guztiak baliogabetzen ditu: mantentze-leihoan egin eta abisatu (denek berriro egin behar dute login).
- `CORS_ORIGINS`: jatorri esplizituak prod-ean; `*` + kredentzialak debekatuta dago eta abiaraztea blokeatzen du.
- Proxy baten atzean: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + aurreko TLS.

## Backup-ak eta migrazioak

- SQLite: kopiatu `*.db` bero geldituta (`-Kill` aurretik). MariaDB: `mariadb-dump` (`db-data` bolumena).
- Migrazioak: `alembic upgrade head` `backend/`-tik (18 bertsio; prod-ean **Alembic soilik**, inoiz ez `create_all`).
- Motor-aldaketa: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); xehetasuna [DATABASE.md](DATABASE.eu.md)-n.

## Arazoen konponbidea

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

## Ikusi halaber

- [USO.md](USO.eu.md): sistemaren abiaraztea eta operazioa
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.eu.md): hedapena, portuak eta CI
- [SEGURIDAD.md](SEGURIDAD.eu.md): gogortze-checklist-a eta politikak
- [../README.md](../README.eu.md): proiektuaren testuinguru orokorra
