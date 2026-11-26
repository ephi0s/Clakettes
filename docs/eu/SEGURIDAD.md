# Segurtasuna — eredua eta checklist-a

[ES](../es/SEGURIDAD.md) · [EN](../en/SEGURIDAD.md) · [FR](../fr/SEGURIDAD.md) · [DE](../de/SEGURIDAD.md) · [IT](../it/SEGURIDAD.md) · [CA](../ca/SEGURIDAD.md) · [EU](SEGURIDAD.md) · [GL](../gl/SEGURIDAD.md) · [OC](../oc/SEGURIDAD.md)

## Token-ak eta saioak

- Access JWT (HS256, 30 min, `type=access`, `jti` bakarra) + refresh opakua (SHA-256 BDn,
  30 egun, erabiltzean errotazioa). Saioa (`UserSession`) IP, gailu,
  iraungitze eta ezeztapenarekin; `last_used_at` lazy 5 min-an behin.
- Purgaketa abiaraztean: ezeztatutako edo duela >30 egun iraungitako saioak ezabatzen dira.
- Balidazio guztia `validate_access_token`-etik pasatzen da (sinadura + mota + saio
  aktiboa); txataren WS-ak ere bai. Saioa ezeztatzeak WS-a ixten du.
- Pasahitzak bcrypt-ekin; CalDAV-ek bearer-a URL-an erabiltzen du (log-etan redaktatuta).
  DAV token-ak 180 egunera iraungitzen dira (`dav_token_expires_at`, birsortgarriak).

## RGPD

- Pribatutasuna lehenetsita: `is_public*` `False`-n (profila, email, bio, kokapena).
- Adostasuna: `privacy_policy_version` + `privacy_accepted_at` kontua sortzean.
- Ahaztea: `DELETE /api/users/me` (eta `DELETE /api/users/{id}` admin/organizer)
  kontua anonimizatzen du, saio/giltza/alias/jakinarazpen/izen-emateak ezabatzen ditu
  eta erreferentziak deslotzen ditu; azken admin aktiboa ezabatzea blokeatzen du.
- Eramangarritasuna: `GET /api/users/me/export` (JSON profila, rolak, izen-emateak,
  mezuak, saioak, etab. dituena).
- Auditoria (5.2 art.): `audit_logs` append-only aktore, ekintza, helburu eta IP-arekin
  ezabaketa, esportazio, rol/etiketetan eta DAV token-etan; irakurketa
  `GET /api/admin/audit-log`-en (admin soilik).
- Igoerak: fitxategi guztia `_save_file`-tik pasatzen da (motak eta magia balidatuta) eta
  identifikatzen duten metadatuak kentzen zaizkio gorde aurretik: EXIF/XMP irudietan
  (Pillow), tag-ak MP4/MOV-n (`ffmpeg -map_metadata -1`, mutagen ffmpeg gabe badago
  ffmpeg), `/Info` PDF-n (pypdf). WebM ffmpeg gabe ezezkoa (422).

## Baimena

| Ámbito | Regla |
|---|---|
| Festival | `require_festival_admin` (admin global u organizer del festival) |
| Canal | `require_channel_admin` (creador/admin) para gestionar; `require_channel_member` para leer privados |
| Grupo de chat | rol `admin` del grupo para borrar; miembro para leer |
| Formulario | `require_form_admin` (creador/admin/organizer) |
| Delegación | delegador o admin para editar/revocar |
| Roles globales | `require_admin(user, db)` bateratua: legatuzko `admin` rola (case-insensitive) edo `UserRole` `ACTIVE`/`APPROVED` egoerarekin; auto-join soilik `attendee` rolaz |
| Alias de usuario | `require_self_or_admin` (jabea edo admin) create/update/delete-n |
| Bloqueos de usuario | `require_owner_or_admin` (jabea edo `can_edit_user`) block/unblock/list/status-en |
| Roles de canal | `Literal[admin,moderator,member]` (422 fuera de lista) |
| Pagos | dueño vía inscripción, admin de festival o global; webhook mock con `MOCK_WEBHOOK_SECRET` |

## Ordainketak

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`; `mock` lehenetsiz `backend/app/config.py`-n). PAN/IBAN gabe BDn: zenbatekoa, moneta, `provider_ref` eta egoera soilik.
- Stripe: SDK nagia + sinadura-egiaztapena (`STRIPE_WEBHOOK_SECRET`).
- Redsys: HMAC_SHA256_V1 sinadura SDK gabe; Bizum `pay_methods="z"`-rekin (alta aurretik merkataritzan). Sandbox-aren aurka balidatu prod aurretik.
- `confirm` eta `refund`-ek `FestivalRegistration.payment_status` (`paid`/`refunded`) sinkronizatzen dute eta, paid denean, `paid_at`/`payment_method`/`transaction_id`; Payment-aren `provider` aktiboaren provider-etik hartzen da, `PAYMENTS_PROVIDER`-etik ez.
- **Egoera erreala**: Stripe eta Redsys ez daude oraindik martxan; haien webhook-ak konektatu behar dira (`POST /api/payments/webhook/{stripe,redsys}`). Gaur egun webhook simulatua baino ez dabil (`POST /api/payments/webhook/mock`).
- Redsys-en `confirm`-ek beti `"pending"` itzultzen du: ez du benetako kobrantzarik baieztatzen webhook-a konektatu arte.

## Perimetroa

- Rate limit SQLite 100/60 s IP bakoitzeko globala, 600/60 s `/dav`-n, 5/300 s login, 20/60 s refresh eta 3/300 s reset eta 60/60 s federazioan. `TESTING` ∈ {1, true, yes, on} (`app.config.is_testing()`) muga guztiak eta auto-migrazioa itzaltzen ditu.
- Goiburuak: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`,
  API-an `Content-Security-Policy` zorrotza (lasaia `/docs`-en soilik),
  `HSTS` ekoizpenean soilik.
- Gorputzak ≤10 MB (413). CORS kredentzialekin eta jatorri esplizituekin.
- MariaDB-k ekoizpenean TLS exijitzen du (`?ssl_ca=…` `DATABASE_URL`-n).

## Ekoizpen-checklist-a

1. `APP_ENV=production`, 64 byte-ko `SECRET_KEY` env bidez (hura gabe ez du abiatzen).
2. `CORS_ORIGINS` domeinu esplizituekin; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS proxy-arekin + `FORWARDED_ALLOW_IPS`; `setup` admin gabe (prod-ez kanpo soilik sortzen da).
4. Aldatu Windows jakinarazpenen `appUserModelId`/GUID-a app-a berrizendatzen bada.

## Gogortzea eta hornidura-katea (11/2026)

- **Mendekotasunen auditoria**: `tools/audit_deps.py`-ek OSV (CVE/GHSA) kontsultatzen du `requirements`, `pubspec.lock` eta venv baterako. Adib.: `python tools/audit_deps.py --requirements backend/requirements.txt --requirements backend/requirements-dev.txt --lock frontend/pubspec.lock --venv backend/.venv --fail-on fixable`. Auditorian python-ecdsa (CVE-2024-23342) ohartarazpen konponezin bat baino ez zen agertu tokiko `.venv`-en; `pip show`-k baieztatzen duenez, ez du paketerik eskatzen eta requirements-en ebazpen garbiak ez du instalatzen, beraz ez da proiektuaren parte.
- **Bertsio finkatuak/adabatuak**: `httpx2>=2.12.0`, `httpcore2>=2.10.0`, `pyasn1>=0.6.5`, `bcrypt==5.0.0`, `pytest==9.2.0`, `icalendar==7.3.2`. Bertsio zuzenak jada libre zeuden OSV ohartarazpenetatik auditatzean.
- **Ekoizpena**: `docker compose --profile prod`-ek `APP_ENV=production`, `SECRET_KEY`, `CORS_ORIGINS` esplizitua, `PUBLIC_BASE_URL` eta `DATABASE_URL` TLS parametroekin eskatzen ditu; abiarazteko balidazioak gako ahulak/komodinak blokeatzen ditu. `start.ps1`-ek ausazko gakoa sortzen du `SECRET_KEY` ez badago (lehen ezagun bat ezartzen zuen).
- **Backend**: middleware-ak eta segurtasun-balidazioa `app/main.py`-tik `app/security.py`-ra eraman ziren; CORS-ek goiburuak mugatzen ditu; docs/redoc/openapi desgaituta ekoizpenean; portabilitate-esportazioak erabiltzaile/admin/nodo federatua egiaztatua eskatzen du; nodo-erregistroak autentifikazioa eskatzen du ekoizpenean; JWKS federatua erregistratutako nodotik baino ez da deskargatzen (anti-SSRF, birzuzenketarik gabe); SSE-k Bearer-a goiburuan onartzen du (query-ko `token` zaharkituta); webhook mock-ek `compare_digest` erabiltzen dute; >72 byte-ko pasahitzak 422-rekin baztertzen dira; bundle-inportazioak profil-eremuak baino ez ditu aplikatzen (inoiz ez `role`/`is_active`/pribatutasuna); SVG-ak CSP sandbox-ekin zerbitzatzen dira.
- **Frontend**: token-ak eta E2EE gakoak `flutter_secure_storage`-en migrazio bakarrarekin (web-ek SharedPreferences erabiltzen du); `UrlLauncherService` helper bakarra `http`/`https`/`mailto`/`tel`/`geo` allowlist-arekin; backend-aren HTTPS balidazioa tokiko garapen-ostalariak izan ezik; logout-ak Hive kutxak eta socket-a garbitzen ditu; CSP `web/index.html`-en eta HSTS/nosniff `nginx.conf`-en.
- **Erreferentziak**: OWASP Top 10 2025 (A02 Konfigurazioa, A03 Hornidura-katea, A05 Injekzioa, A07 Autentifikazioa) eta OWASP MASVS Flutter-erako.

## Federazioa (2-10 faseak)

Xehetasun osoa [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) fitxategian. Indarrean dauden kontrolak:

- Nodoaren identitatea = domeinua + TLS ziurtagiria. Peering elkarrekikoa mTLS bidez domeinu-ziurtagiriekin (CA publikoa edo pribatua); TLS nahitaezkoa, self-signed-ik ez prod-en.
- RSA-SHA256 sinatutako manifestua norberaren PEM/gakoarekin eta 24 h-ko `expires_at`-arekin; `whoami`-k federazio-JWTa eskatzen du; JWKS pareen tokenak balioztatzeko; `peers/verify` eta `peers/revoke`.
- Nodo bakoitzeko `allowlist`/`blocklist` (`node_policies`), `import_only`, `disable_chat` eta `disable_search`-ekin. Rate limiting eta anti-flood ertzean; moderazio-txostenen hedapena.
- Portabilitatea: HMAC eta checksum-ekin sinatutako bundle-ak; inportazioak `MediaUrl` balioztatu/saneatzen du eta `contest_type` normalizatzen du; jaialdi eta identitate migrazioa `identity_redirects`-ekin eta `migration_audits`-en auditoriarekin; migrazio-endpoint-ek admin eskatzen dute.
- Txat federatua: RS256 sinatutako bridge-a, `message_id` bidez dedup-a `chat_outbox`-en, `timestamp` bidez ordena; txostenak eta isiltzeak, hitz-iragazkia eta 10 mezu/60 s-ko muga nodo eta erabiltzaile bakoitzeko.
- Gertaerak: HMAC bidez sinatutako argitalpena (`X-Clakettes-Signature`), SSE Bearer-arekin goiburuan (query-ko `token` zaharkituta), `since` eta `limit` aukerakoekin, 200-ko replay-a eta 3 birsaio atzerapenarekin.
- Erresilientzia: `/api/federation/resilience/health`, `/heartbeat`, `/metrics` (p50/p95), gakoen errebokazioa (`keys/revoke`) eta 8 urratseko intzidente-plana. Birzirkulazioa/errebokazioa ziurtagiria berrituz; nodo arriskutu bat direktoriotik baliogabetzen da.
