# Seguranca — model e checklist

[ES](../es/SEGURIDAD.md) · [EN](../en/SEGURIDAD.md) · [FR](../fr/SEGURIDAD.md) · [DE](../de/SEGURIDAD.md) · [IT](../it/SEGURIDAD.md) · [CA](../ca/SEGURIDAD.md) · [EU](../eu/SEGURIDAD.md) · [GL](../gl/SEGURIDAD.md) · [OC](SEGURIDAD.md)

## Tokens e sessions

- Access JWT (HS256, 30 min, `type=access`, `jti` unic) + refresh opac (SHA-256 en BD, 30 d, rotacion al usar). Sesion (`UserSession`) amb IP, dispositiu, expiracio i revocacio; `last_used_at` lazy cada 5 min.
- Purgat a l'arrancada: s'eliminen sessions revocades o caducades fa >30 d.
- Toda validacio passa per `validate_access_token` (signatura + tipus + sessio activa); el WS del xat també. Revocar una sessio tanca el WS.
- Contrasenyes amb bcrypt; CalDAV usa bearer a l'URL (redactat als logs). Els tokens DAV caduquen als 180 dies (`dav_token_expires_at`, regenerables).

## RGPD

- Privacitat per defecte: `is_public*` en `False` (perfil, correu, bio, ubicacio).
- Consentiment: `privacy_policy_version` + `privacy_accepted_at` al crear el compte.
- Olvido: `DELETE /api/users/me` (i `DELETE /api/users/{id}` admin/organizer) anonimatza el compte, esborra sessions/claus/alias/notificacions/inscripcions i desvincula referencies; bloqueja esborrar el darrer admin actiu.
- Portabilitat: `GET /api/users/me/export` (JSON amb perfil, rols, inscripcions, missatges, sessions, etc.).
- Auditoria (art. 5.2): `audit_logs` append-only amb actor, accio, objectiu i IP en esborrades, exportacions, rols/etiquetes i tokens DAV; lectura en `GET /api/admin/audit-log` (solament admin).
- Pujades: tot fitxer passa per `_save_file` (tipus i magia validats) i s'eliminen metadades identificatives abans de desar: EXIF/XMP a imatges (Pillow), etiquetes a MP4/MOV (`ffmpeg -map_metadata -1`, mutagen si no hi ha ffmpeg), `/Info` a PDF (pypdf). WebM sense ffwxénese rebutja (422).

## Autorizacio

| Ambito | Regla |
|--------|-------|
| Festival | `require_festival_admin` (admin global u organizer del festival) |
| Canal | `require_channel_admin` (creador/admin) per gestionar; `require_channel_member` per llegir privats |
| Grup de xat | rol `admin` del grup per esborrar; membre per llegir |
| Formulari | `require_form_admin` (creador/admin/organizer) |
| Delegacio | delegant o admin per editar/revocar |
| Rols globals | `require_admin(user, db)` unificat: ròtle legacy `admin` (case-insensitive) o `UserRole` amb estat `ACTIVE`/`APPROVED`; auto-join solament amb ròtle `attendee` |
| Alias d'usagi | `require_self_or_admin` (proprietari o admin) en create/update/delete |
| Blocatges d'usagi | `require_owner_or_admin` (proprietari o `can_edit_user`) en block/unblock/list/status |
| Rols de canal | `Literal[admin,moderator,member]` (422 fora de la llista) |
| Pagaments | propietari via inscripcio, admin de festival o global; webhook mock amb `MOCK_WEBHOOK_SECRET` |

## Pagaments

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`; `mock` per defaut en `backend/app/config.py`). Sense PAN/IBAN a la BD: solament import, moneda, `provider_ref` i estat.
- Stripe: SDK perezos + verificacio de signatura (`STRIPE_WEBHOOK_SECRET`).
- Redsys: signatura HMAC_SHA256_V1 sense SDK; Bizum amb `pay_methods="z"` (alta prealable al comerç). Validar contra el sandbox abans de prod.
- `confirm` e `refund` sincronizan `FestivalRegistration.payment_status` (`paid`/`refunded`) e, en paid, `paid_at`/`payment_method`/`transaction_id`; lo `provider` del Payment se pren del provider actiu, non de `PAYMENTS_PROVIDER`.
- **Estat real**: Stripe e Redsys NO son pas encara operatius; manca cablar lors webhooks (`POST /api/payments/webhook/{stripe,redsys}`). Uei solament lo webhook simulat fonciona (`POST /api/payments/webhook/mock`).
- Lo `confirm` de Redsys torna sempre `"pending"`: non confirma de pagaments reaus fins que lo webhook siá cablat.

## Perimetre

- Rate limit SQLite 100/60 s per IP global, 600/60 s en `/dav`, 5/300 s login, 20/60 s refresh e 3/300 s reset e 60/60 s en federacion. `TESTING` ∈ {1, true, yes, on} (`app.config.is_testing()`) desactiva totes los limits e l'auto-migracion.
- Capçaleres: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy` estricta a l'API (relajada només a `/docs`), `HSTS` solament a produccio.
- Corcos <=10 MB (413). CORS amb credencials i orígens explicitos.
- MariaDB a produccio exigeix TLS (`?ssl_ca=…` a `DATABASE_URL`).

## Llista de comprovacio de productiu

1. `APP_ENV=production`, `SECRET_KEY` de 64 bytes per env (sense ella no arranca).
2. `CORS_ORIGINS` amb dominis explicitos; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS amb proxy + `FORWARDED_ALLOW_IPS`; sense admin `setup` (solament es crea fora de prod).
4. Canvia el `appUserModelId`/GUID de notificacions Windows si es renombra l'aplicacio.

## Endurciment e cadena d'aprovesiment (11/2026)

- **Auditoria de las dependéncias**: `tools/audit_deps.py` consulta OSV (CVE/GHSA) per a `requirements`, `pubspec.lock` e un venv. Ex.: `python tools/audit_deps.py --requirements backend/requirements.txt --requirements backend/requirements-dev.txt --lock frontend/pubspec.lock --venv backend/.venv --fail-on fixable`. Pendant l'auditoria es presentèt un avís irreparable de python-ecdsa (CVE-2024-23342) solament dins lo `.venv` local ; `pip show` confirma que cap paquet lo demanda e una resolucion neta dels requirements l'installa pas : es fa pas partida del projècte.
- **Versions fixadas/patchadas**: `httpx2>=2.12.0`, `httpcore2>=2.10.0`, `pyasn1>=0.6.5`, `bcrypt==5.0.0`, `pytest==9.2.0`, `icalendar==7.3.2`. Las versions directas èran ja sens avis OSV al moment de l'auditoria.
- **Produccion**: `docker compose --profile prod` exigeix `APP_ENV=production`, `SECRET_KEY`, `CORS_ORIGINS` explicit, `PUBLIC_BASE_URL` e `DATABASE_URL` amb parametres TLS; la validacion a l'arrancada bloca las claus feblas/comodin. `start.ps1` genera una clau aleatòria se `SECRET_KEY` manca (abans ne fixava una coneguda).
- **Backend**: middleware e validacion de seguretat desplaçats de `app/main.py` a `app/security.py`; CORS restrén los en-tèstas; docs/redoc/openapi desactivats en produccion; l'exportacion de portabilitat exigeix usagi/admin/nose federat verificat; l'enregistrament de noses exigeix autentificacion en produccion; lo JWKS federat se telecarga solament dempuèi noses enregistrats (anti-SSRF, sens redireccions); SSE accepta Bearer dins l'en-tèsta (`token` en query deprecat); webhooks mock amb `compare_digest`; contrasenhas >72 octets regetadas amb 422; l'importacion de bundles aplica solament los camps de perfil (jamai `role`/`is_active`/vida privada); SVG servits amb CSP sandbox.
- **Frontend**: tokens e claus E2EE dins `flutter_secure_storage` amb migracion unica (lo web utiliza SharedPreferences); helper unic `UrlLauncherService` amb allowlist `http`/`https`/`mailto`/`tel`/`geo`; validacion HTTPS del backend fòra dels òstes locals de desvolopament; lo logout purga las bòstias Hive e lo socket; CSP dins `web/index.html` e HSTS/nosniff dins `nginx.conf`.
- **Referéncias**: OWASP Top 10 2025 (A02 Configuracion, A03 Cadena d'aprovesiment, A05 Injeccion, A07 Autentificacion) e OWASP MASVS per a Flutter.

## Federacio (fasas 2-10)

Detalh complet dins [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md). Contròls vigents:

- Identitat de nose = domeni + certificat TLS. Peering mutu via mTLS amb certificats de domeni (CA publica o privada); TLS obligatòri, sens self-signed en prod.
- Manifèst signat RSA-SHA256 amb PEM/clau pròpris e `expires_at` de 24 h; `whoami` exigís JWT federat; JWKS per verificar los tokens dels pares; `peers/verify` e `peers/revoke`.
- `allowlist`/`blocklist` per nose (`node_policies`), amb `import_only`, `disable_chat` e `disable_search`. Rate limiting e anti-inundada al marge; propagacion dels rapòrts de moderacion.
- Portabilitat: bundles signats amb HMAC e checksum; l'import valida/sanea `MediaUrl` e normaliza `contest_type`; migracion de festivals e identitats amb `identity_redirects` e auditoria dins `migration_audits`; los endpoints de migracion exigisson admin.
- Chat federat: bridge signat RS256, dedup per `message_id` dins `chat_outbox`, ordre per `timestamp`; rapòrts e silencis, filtre de mots e limita de 10 messatges/60 s per nose e usagi.
- Eveniments: publicacion signada amb HMAC (`X-Clakettes-Signature`), SSE amb Bearer dins l'en-tèsta (`token` en query deprecat), `since` e `limit` opcionalas, replay de 200 e 3 reensajos amb backoff.
- Resiliéncia: `/api/federation/resilience/health`, `/heartbeat`, `/metrics` (p50/p95), revocacion de claus (`keys/revoke`) e plan d'incident en 8 etapas. Rotacion/revocacion per renovacion del certificat; un nose compromés es invalidat dins lo directòri.