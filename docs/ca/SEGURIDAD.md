# Seguretat — model i llista de comprovacio

[ES](../es/SEGURIDAD.md) · [EN](../en/SEGURIDAD.md) · [FR](../fr/SEGURIDAD.md) · [DE](../de/SEGURIDAD.md) · [IT](../it/SEGURIDAD.md) · [CA](SEGURIDAD.md) · [EU](../eu/SEGURIDAD.md) · [GL](../gl/SEGURIDAD.md) · [OC](../oc/SEGURIDAD.md)

## Tokens i sessions

- Access JWT (HS256, 30 min, `type=access`, `jti` unic) + refresh opac (SHA-256 a la BD, 30 d, rotacio al usar). Sessio (`UserSession`) amb IP, dispositiu, expiracio i revocacio; `last_used_at` lazy cada 5 min.
- Purgat a l'arrancada: s'eliminen sessions revocades o caducades fa >30 d.
- Tota validacio passa per `validate_access_token` (signatura + tipus + sessio activa); el WS del xat també. Revocar una sessio tanca el WS.
- Contrasenyes amb bcrypt; CalDAV utilitza bearer a l'URL (redactat als logs). Els tokens DAV caduquen als 180 dies (`dav_token_expires_at`, regenerables).

## RGPD

- Privacitat per defecte: `is_public*` en `False` (perfil, correu, bio, ubicacio).
- Consentiment: `privacy_policy_version` + `privacy_accepted_at` al crear el compte.
- Oblit: `DELETE /api/users/me` (i `DELETE /api/users/{id}` admin/organizer) anonimatza el compte, esborra sessions/claus/alias/notificacions/inscripcions i desvincula referencies; bloqueja esborrar el darrer admin actiu.
- Portabilitat: `GET /api/users/me/export` (JSON amb perfil, rols, inscripcions, missatges, sessions, etc.).
- Auditoria (art. 5.2): `audit_logs` append-only amb actor, accio, objectiu i IP en esborrades, exportacions, rols/etiquetes i tokens DAV; lectura en `GET /api/admin/audit-log` (només admin).
- Pujades: tot fitxer passa per `_save_file` (tipus i magia validats) i s'eliminen metadades identificatives abans de desar: EXIF/XMP a imatges (Pillow), etiquetes a MP4/MOV (`ffmpeg -map_metadata -1`, mutagen si no hi ha ffmpeg), `/Info` a PDF (pypdf). WebM sense ffmpeg es rebutja (422).

## Autoritzacio

| Ambit | Regla |
|-------|-------|
| Festival | `require_festival_admin` (admin global u organizer del festival) |
| Canal | `require_channel_admin` (creador/admin) per gestionar; `require_channel_member` per llegir privats |
| Grup de xat | rol `admin` del grup per esborrar; membre per llegir |
| Formulari | `require_form_admin` (creador/admin/organizer) |
| Delegacio | delegant o admin per editar/revocar |
| Rols globals | `require_admin(user, db)` unificat: rol legacy `admin` (case-insensitive) o `UserRole` amb estat `ACTIVE`/`APPROVED`; auto-join nomes amb rol `attendee` |
| Alias d'usuari | `require_self_or_admin` (propietari o admin) a create/update/delete |
| Bloquejos d'usuari | `require_owner_or_admin` (propietari o `can_edit_user`) a block/unblock/list/status |
| Rols de canal | `Literal[admin,moderator,member]` (422 fora de la llista) |
| Pagaments | propietari via inscripcio, admin de festival o global; webhook mock amb `MOCK_WEBHOOK_SECRET` |

## Pagaments

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`; `mock` per defecte a `backend/app/config.py`). Sense PAN/IBAN a la BD: solament import, moneda, `provider_ref` i estat.
- Stripe: SDK perezos + verificacio de signatura (`STRIPE_WEBHOOK_SECRET`).
- Redsys: signatura HMAC_SHA256_V1 sense SDK; Bizum amb `pay_methods="z"` (alta prealable al comerç). Validar contra el sandbox abans de prod.
- `confirm` i `refund` sincronitzen `FestivalRegistration.payment_status` (`paid`/`refunded`) i, en paid, `paid_at`/`payment_method`/`transaction_id`; el `provider` del Payment es pren del provider actiu, no de `PAYMENTS_PROVIDER`.
- **Estat real**: Stripe i Redsys NO estan operatius encara; falta cablejar els seus webhooks (`POST /api/payments/webhook/{stripe,redsys}`). Ara només funciona el webhook simulat (`POST /api/payments/webhook/mock`).
- El `confirm` de Redsys retorna sempre `"pending"`: no confirma cobraments reals fins que es cablegi el webhook.

## Perimetre

- Rate limit SQLite 100/60 s per IP global, 600/60 s a `/dav`, 5/300 s login, 20/60 s refresh i 3/300 s reset i 60/60 s en federació. `TESTING` ∈ {1, true, yes, on} (`app.config.is_testing()`) apaga tots els límits i l'auto-migració.
- Capçaleres: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy` estricta a l'API (relajada només a `/docs`), `HSTS` solament a produccio.
- Cosos <=10 MB (413). CORS amb credencials i orígens explicitos.
- MariaDB a produccio exigeix TLS (`?ssl_ca=…` a `DATABASE_URL`).

## Llista de comprovacio de producció

1. `APP_ENV=production`, `SECRET_KEY` de 64 bytes per env (sense ella no arranca).
2. `CORS_ORIGINS` amb dominis explicitos; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS amb proxy + `FORWARDED_ALLOW_IPS`; sense admin `setup` (nomes es crea fora de prod).
4. Canvia el `appUserModelId`/GUID de notificacions Windows si es renombra l'aplicacio.

## Enduriment i cadena de subministrament (11/2026)

- **Auditoria de dependències**: `tools/audit_deps.py` consulta OSV (CVE/GHSA) per a `requirements`, `pubspec.lock` i un venv. Ex.: `python tools/audit_deps.py --requirements backend/requirements.txt --requirements backend/requirements-dev.txt --lock frontend/pubspec.lock --venv backend/.venv --fail-on fixable`. Durant l'auditoria va aparèixer un avís irreparable de python-ecdsa (CVE-2024-23342) únicament al `.venv` local; `pip show` confirma que cap paquet no el requereix i una resolució neta dels requirements no l'instal·la, per la qual cosa no forma part del projecte.
- **Versions fixades/parchejades**: `httpx2>=2.12.0`, `httpcore2>=2.10.0`, `pyasn1>=0.6.5`, `bcrypt==5.0.0`, `pytest==9.2.0`, `icalendar==7.3.2`. Les versions directes ja estaven lliures d'avisos OSV en fer l'auditoria.
- **Producció**: `docker compose --profile prod` exigeix `APP_ENV=production`, `SECRET_KEY`, `CORS_ORIGINS` explícit, `PUBLIC_BASE_URL` i `DATABASE_URL` amb paràmetres TLS; la validació a l'arrancada bloqueja claus febles/comodí. `start.ps1` genera una clau aleatòria si no hi ha `SECRET_KEY` (abans en fixava una coneguda).
- **Backend**: middleware i validació de seguretat moguts de `app/main.py` a `app/security.py`; CORS restringeix capçaleres; docs/redoc/openapi desactivats en producció; l'exportació de portabilitat exigeix usuari/admin/node federat verificat; el registre de nodes exigeix autenticació en producció; el JWKS federat només es descarrega de nodes registrats (anti-SSRF, sense redireccions); SSE accepta Bearer a la capçalera (`token` a query obsolet); webhooks mock amb `compare_digest`; contrasenyes >72 bytes rebutjades amb 422; la importació de bundles només aplica camps de perfil (mai `role`/`is_active`/privacitat); SVG servits amb CSP sandbox.
- **Frontend**: tokens i claus E2EE a `flutter_secure_storage` amb migració única (el web fa servir SharedPreferences); helper únic `UrlLauncherService` amb allowlist `http`/`https`/`mailto`/`tel`/`geo`; validació HTTPS del backend llevat d'hosts locals de desenvolupament; el logout buida les caixes Hive i el socket; CSP a `web/index.html` i HSTS/nosniff a `nginx.conf`.
- **Referències**: OWASP Top 10 2025 (A02 Configuració, A03 Cadena de subministrament, A05 Injecció, A07 Autenticació) i OWASP MASVS per a Flutter.

## Federacio (fases 2-10)

Detall complet a [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md). Controls vigents:

- Identitat de node = domini + certificat TLS. Peering mutu via mTLS amb certificats de domini (CA publica o privada); TLS obligatori, sense self-signed a prod.
- Manifest signat RSA-SHA256 amb PEM/clau propis i `expires_at` de 24 h; `whoami` exigeix JWT federat; JWKS per verificar tokens de pares; `peers/verify` i `peers/revoke`.
- `allowlist`/`blocklist` per node (`node_policies`), amb `import_only`, `disable_chat` i `disable_search`. Rate limiting i anti-inundada al marge; propagacio d'informes de moderacio.
- Portabilitat: bundles signats amb HMAC i checksum; import valida/sanea `MediaUrl` i normalitza `contest_type`; migracio de festivals i identitats amb `identity_redirects` i auditoria a `migration_audits`; els endpoints de migracio exigeixen admin.
- Xat federat: bridge signat RS256, dedup per `message_id` a `chat_outbox`, ordre per `timestamp`; reportes i silenciaments, filtre de paraules i limit de 10 missatges/60 s per node i usuari.
- Esdeveniments: publicacio signada amb HMAC (`X-Clakettes-Signature`), SSE amb Bearer a la capçalera (`token` a query obsolet), `since` i `limit` opcionals, replay de 200 i 3 reintents amb backoff.
- Resiliencia: `/api/federation/resilience/health`, `/heartbeat`, `/metrics` (p50/p95), revocacio de claus (`keys/revoke`) i pla d'incident en 8 passos. Rotacio/revocacio per renovacio del certificat; un node compromes s'invalida al directori.