# Administrazioa — Clakettes

[ES](../es/ADMINISTRACION.md) · [EN](../en/ADMINISTRACION.md) · [FR](../fr/ADMINISTRACION.md) · [DE](../de/ADMINISTRACION.md) · [IT](../it/ADMINISTRACION.md) · [CA](../ca/ADMINISTRACION.md) · [EU](ADMINISTRACION.md) · [GL](../gl/ADMINISTRACION.md) · [OC](../oc/ADMINISTRACION.md)

Inplementazio bat operatzen duenarentzako gida. Azpiegitura [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) fitxategian, ekoizpenerako kontrol-zerrenda [SEGURIDAD.md](SEGURIDAD.md) fitxategian.

## Hasierako kontua

Ekoizpenean ez denean (`APP_ENV != production`), abiarazteak `admin` / `setup` sortzen du (`admin@clakettes.com`, admin rola) lehendik ez badago; prod-en **ez da sortzen**. Aldatu pasahitza sartzean. Alta `POST /api/users/login` bidez egiten da (JWT 30 min + refresh 30 d, saioak `/api/auth/sessions`-en zerrendatu eta errebokatu).

## `/api/admin` endpoint-ak (soilik admin rola, bestela 403)

| Metodoa eta ibilbidea | Eragina |
|---|---|
| `GET /api/admin/stats` | Kontagailuak: erabiltzaileak, jaialdiak, film laburrak, mezuak, aktiboak |
| `GET /api/admin/tables` | Taulak (`alembic_version` izan ezik) errenkada-kopuruarekin |
| `GET /api/admin/audit-log` | Auditoretza-aztarna (`action`, `actor_user_id` iragazkiak) |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 `confirm` `yes` ez bada, 403 pasahitza egiaztatzen ez bada; berezko rate-limit 3/300s (429, `TESTING=true` bidez saihestuta) |

## Sekretuak eta birzirkulazioa

- `SECRET_KEY`: nahitaezkoa prod-en (abiarazteak adibidekoarekin huts egiten du eta `secrets.token_urlsafe(64)` adierazten du). Birzirkulatzeak JWT eta refresh token guztiak baliogabetzen ditu: egin mantentze-leiho batean eta jakinarazi (denek berriro egin behar dute login).
- `CORS_ORIGINS`: jatorri esplizituak prod-en; `*` + kredentzialak debekatuta dago eta abiaraztea blokeatzen du.
- Proxy atzean: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + aurreko TLS.

## Federazioa

| Eragiketa | Endpoint / tresna | Eragina |
|---|---|---|
| Nodoak eta politikak | `GET/POST /api/federation/nodes` | Allowlist/blocklist `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search` eremuekin (admin) |
| Parearen identitatea | `GET /api/federation/whoami` | Parearen RS256 JWTa bere JWKSen kontra balioztatzen du; 401 baliozkoa ez bada |
| Portabilitatea | `POST /api/federation/portability/bundles`, `/imports`, `/festivals/{id}/migrate`, `/users/{ref}/migrate`, `GET /redirects/{ref}` | Sinatutako bundle-ak esportatu/inportatu, jabetza eta identitatea migratu eta erreferentzia zaharrak ebaztu (migrazioak soilik admin) |
| Txata eta moderazioa | `/api/federation/chat/bridge/{inbound,outbound,config}`, `GET /api/federation/chat/messages`, `/api/chat/moderation/*` | Sinatutako bridge-a, deduplikatutako historia, txostenak, isiltzeak, iragazkia eta 10 mezu/60 s nodo eta erabiltzaile bakoitzeko |
| Gertaerak | `GET /api/federation/events/stream`, `POST /publish`, `GET /retry-queue` | SSE `since` eta bihotz-taupadarekin, pareei argitaratzea eta birsaioak (3 saiakera, 300 ms → 1,5 s → 5 s) |
| Erresilientzia | `GET /api/federation/resilience/{health,heartbeat,metrics,incident-plan}`, `POST /keys/revoke`, `GET /keys/revoked` | Osasuna, taupada, p50/p95 metrikak, gakoen berehalako errebokazioa eta intzidente-plana |
| Betetzea | `python tools/federation_conformance.py <url> [--json]` | Hirugarren nodo bat egiaztatzen du; 1 itzultzen du hutsegite kritiko edo altuak badaude |

Konfiantza-ereduaren eta garraioaren xehetasuna [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) eta [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md) fitxategietan dago.

## Babeskopiak eta migrazioak

- SQLite: kopiatu `*.db` beroa geldituta (`-Kill` lehenago). MariaDB: `mariadb-dump` (`db-data` bolumena).
- Migrazioak: `alembic upgrade head` `backend/`-tik (prod-en **soilik** Alembic, inoiz ez `create_all`). Azken migrazioek `identity_redirects`, `migration_audits`, `chat_outbox`, `message_reports`, `chat_mutes`, eserlekuaren bakartasuna (`uq_event_seat_location`) eta `festival_id` nahitaezkoarekin `contest_type` laburretan gehitzen dituzte.
- Motor-aldaketa: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); xehetasuna [DATABASE.md](DATABASE.md) fitxategian.

## Arazoak konpontzen

| Sintoma | Kausa probablea | Ekintza |
|---|---|---|
| Abiaraztea `SECRET_KEY` / CORS-engatik eteten da | prod-en default segurua edo `*` | Definitu `SECRET_KEY` eta `CORS_ORIGINS` esplizituak |
| `401` formularioen endpoint publikoetan | esteka gaizki sortuta | Berrikusi estekaren tokena; sarbide anonimoak berez ez du 401 ematen |
| `403` jaialdia/kanala/batzordea kudeatzean | deitzaileak ez du rolak | Egiaztatu kidetza eta rola (`GET …/members`); auto-join-ek soilik `attendee` ematen du |
| `409` batzean | dagoeneko kidea da | Erabili `leave` edo kudeatu kideetatik |
| `413` igotzean | 10 MB gorputza / 5 MB irudia / 100 MB bideoa / 10 MB pdf gainditzen du | Konprimitu edo zatitu fitxategia |
| `429` orokortua | 100/60s IP bakoitzeko (edo 3/300s reset-ean) | Itxaron eta saiatu berriro; berrikusi `TESTING=true` hondarra |
| WS ez da konektatzen | JWTa `type=access` gabe edo saioa errebokatu/iraungita | Login berria egin; berrikusi `/api/auth/sessions` |
| Lineaz kanpoko app-a ez da sinkronizatzen | ilara agortutako hutsegiteekin (`failed`, 3 saiakera + atzerapena) | Berrikusi erroreak sinkronizazio-abisuan; `clear()` logout-ean berretsi ondoren |
| `403` bundle-a inportatzean | `origin_domain` ez dago baimenduta nodoaren politikan | Berrikusi `/api/federation/nodes` eta inportatu berriro |
| `429` txat federatuak | 10 mezu baino gehiago/60 s nodo eta erabiltzaile bakoitzeko | Itxaron `Retry-After` arte; testetan `TESTING=true` bidez desaktibatzen da |
| SSE gertaerak moztuta edo daturik gabe | token baliogabea edo `since` replay-a baino aurrerago | Login berria egin eta `since=0`-ekin berrabiarazi (200 gertaeraren replay-a) |
| Mezu federalak bikoiztuta | bridge-aren birbidaltzea | `message_id` bidez baztertzen dira `chat_outbox`-en; berrikusi `/api/federation/chat/messages` |

## Ikus ere

- [USO.md](USO.md): sistemaren abiaraztea eta operazioa
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): inplementazioa, atak eta CI
- [SEGURIDAD.md](SEGURIDAD.md): gogortze-zerrenda eta politikak
- [../README.eu.md](../../README.eu.md): proiektuaren testuinguru orokorra
