# Sicurezza — modello e checklist

[ES](../es/SEGURIDAD.md) · [EN](../en/SEGURIDAD.md) · [FR](../fr/SEGURIDAD.md) · [DE](../de/SEGURIDAD.md) · [IT](SEGURIDAD.md) · [CA](../ca/SEGURIDAD.md) · [EU](../eu/SEGURIDAD.md) · [GL](../gl/SEGURIDAD.md) · [OC](../oc/SEGURIDAD.md)

## Token e sessioni

- Access JWT (HS256, 30 min, `type=access`, `jti` unico) + refresh opaco (SHA-256 nel DB,
  30 g, rotazione all'uso). Sessione (`UserSession`) con IP, dispositivo,
  scadenza e revoca; `last_used_at` lazy ogni 5 min.
- Purga all'avvio: si eliminano sessioni revocate o scadute da >30 g.
- Tutta la validazione passa per `validate_access_token` (firma + tipo + sessione
  attiva); anche il WS della chat. Revocare la sessione chiude il WS.
- Password con bcrypt; CalDAV usa bearer in URL (redatto nei log).
  I token DAV scadono a 180 giorni (`dav_token_expires_at`, rigenerabili).

## RGPD

- Privacy di default: `is_public*` a `False` (profilo, email, bio, posizione).
- Consenso: `privacy_policy_version` + `privacy_accepted_at` alla creazione dell'account.
- Oblio: `DELETE /api/users/me` (e `DELETE /api/users/{id}` admin/organizer)
  anonimizza l'account, cancella sessioni/chiavi/alias/notifiche/iscrizioni
  e scollega i riferimenti; blocca la cancellazione dell'ultimo admin attivo.
- Portabilità: `GET /api/users/me/export` (JSON con profilo, ruoli, iscrizioni,
  messaggi, sessioni, ecc.).
- Audit (art. 5.2): `audit_logs` append-only con attore, azione, obiettivo e IP
  in cancellazioni, esportazioni, ruoli/tag e token DAV; lettura in
  `GET /api/admin/audit-log` (solo admin).
- Upload: ogni file passa per `_save_file` (tipi e magia validati) e gli si
  eliminano i metadati identificativi prima di salvare: EXIF/XMP nelle immagini
  (Pillow), tag in MP4/MOV (`ffmpeg -map_metadata -1`, mutagen se non c'è
  ffmpeg), `/Info` in PDF (pypdf). WebM senza ffmpeg si rifiuta (422).

## Autorizzazione

| Ámbito | Regla |
|---|---|
| Festival | `require_festival_admin` (admin global u organizer del festival) |
| Canal | `require_channel_admin` (creador/admin) para gestionar; `require_channel_member` para leer privados |
| Grupo de chat | rol `admin` del grupo para borrar; miembro para leer |
| Formulario | `require_form_admin` (creador/admin/organizer) |
| Delegación | delegador o admin para editar/revocar |
| Roles globales | `require_admin(user, db)` unificato: ruolo legacy `admin` (case-insensitive) o `UserRole` con stato `ACTIVE`/`APPROVED`; auto-join solo con ruolo `attendee` |
| Alias de usuario | `require_self_or_admin` (proprietario o admin) in create/update/delete |
| Bloqueos de usuario | `require_owner_or_admin` (proprietario o `can_edit_user`) in block/unblock/list/status |
| Roles de canal | `Literal[admin,moderator,member]` (422 fuera de lista) |
| Pagos | dueño vía inscripción, admin de festival o global; webhook mock con `MOCK_WEBHOOK_SECRET` |

## Pagamenti

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`; `mock` per impostazione predefinita in `backend/app/config.py`). Senza PAN/IBAN nel DB: solo importo, valuta, `provider_ref` e stato.
- Stripe: SDK pigro + verifica della firma (`STRIPE_WEBHOOK_SECRET`).
- Redsys: firma HMAC_SHA256_V1 senza SDK; Bizum con `pay_methods="z"` (attivazione previa nel commercio). Validare contro il sandbox prima di prod.
- `confirm` e `refund` sincronizzano `FestivalRegistration.payment_status` (`paid`/`refunded`) e, in paid, `paid_at`/`payment_method`/`transaction_id`; il `provider` del Payment è preso dal provider attivo, non da `PAYMENTS_PROVIDER`.
- **Stato reale**: Stripe e Redsys NON sono ancora operativi; manca il collegamento dei loro webhook (`POST /api/payments/webhook/{stripe,redsys}`). Oggi funziona solo il webhook simulato (`POST /api/payments/webhook/mock`).
- Il `confirm` di Redsys restituisce sempre `"pending"`: non conferma pagamenti reali finché il webhook non è collegato.

## Perimetro

- Rate limit SQLite 100/60 s per IP globale, 600/60 s su `/dav`, 5/300 s login, 20/60 s refresh e 3/300 s reset e 60/60 s in federazione. `TESTING` ∈ {1, true, yes, on} (`app.config.is_testing()`) disattiva tutti i limiti e l'auto-migrazione.
- Header: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`,
  `Content-Security-Policy` stretta nell'API (rilassata solo in `/docs`),
  `HSTS` solo in produzione.
- Corpi ≤10 MB (413). CORS con credenziali e origini esplicite.
- MariaDB in produzione esige TLS (`?ssl_ca=…` in `DATABASE_URL`).

## Checklist produzione

1. `APP_ENV=production`, `SECRET_KEY` da 64 byte via env (senza di essa non si avvia).
2. `CORS_ORIGINS` con domini espliciti; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS con proxy + `FORWARDED_ALLOW_IPS`; senza admin `setup` (si crea solo fuori prod).
4. Cambiare `appUserModelId`/GUID delle notifiche Windows se si rinomina l'app.

## Indurimento e catena di fornitura (11/2026)

- **Audit delle dipendenze**: `tools/audit_deps.py` interroga OSV (CVE/GHSA) per `requirements`, `pubspec.lock` e un venv. Es.: `python tools/audit_deps.py --requirements backend/requirements.txt --requirements backend/requirements-dev.txt --lock frontend/pubspec.lock --venv backend/.venv --fail-on fixable`. Durante l'audit è comparso un avviso non correggibile relativo a python-ecdsa (CVE-2024-23342) solo nel `.venv` locale; `pip show` conferma che nessun pacchetto lo richiede e una risoluzione pulita dei requirements non lo installa, quindi non fa parte del progetto.
- **Versioni fissate/patchate**: `httpx2>=2.12.0`, `httpcore2>=2.10.0`, `pyasn1>=0.6.5`, `bcrypt==5.0.0`, `pytest==9.2.0`, `icalendar==7.3.2`. Le versioni dirette erano già senza avvisi OSV al momento dell'audit.
- **Produzione**: `docker compose --profile prod` richiede `APP_ENV=production`, `SECRET_KEY`, `CORS_ORIGINS` esplicito, `PUBLIC_BASE_URL` e `DATABASE_URL` con parametri TLS; la validazione all'avvio blocca chiavi deboli/jolly. `start.ps1` genera una chiave casuale se `SECRET_KEY` è assente (prima ne impostava una nota).
- **Backend**: middleware e validazione di sicurezza spostati da `app/main.py` a `app/security.py`; CORS limita gli header; docs/redoc/openapi disattivati in produzione; l'export di portabilità richiede utente/admin/nodo federato verificato; la registrazione dei nodi richiede autenticazione in produzione; il JWKS federato viene scaricato solo da nodi registrati (anti-SSRF, senza redirect); SSE accetta Bearer nell'header (query `token` deprecato); webhook mock con `compare_digest`; password >72 byte rifiutate con 422; l'import dei bundle applica solo i campi del profilo (mai `role`/`is_active`/privacy); SVG serviti con CSP sandbox.
- **Frontend**: token e chiavi E2EE in `flutter_secure_storage` con migrazione unica (il web usa SharedPreferences); helper unico `UrlLauncherService` con allowlist `http`/`https`/`mailto`/`tel`/`geo`; validazione HTTPS del backend tranne host locali di sviluppo; il logout purga le box Hive e il socket; CSP in `web/index.html` e HSTS/nosniff in `nginx.conf`.
- **Riferimenti**: OWASP Top 10 2025 (A02 Configurazione, A03 Catena di fornitura, A05 Iniezione, A07 Autenticazione) e OWASP MASVS per Flutter.

## Federazione (fasi 2-10)

Dettaglio completo in [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md). Controlli attivi:

- Identità del nodo = dominio + certificato TLS. Peering reciproco via mTLS con certificati di dominio (CA pubblica o privata); TLS obbligatorio, nessun self-signed in prod.
- Manifesto firmato RSA-SHA256 con PEM/chiave propri e `expires_at` di 24 h; `whoami` richiede JWT federato; JWKS per verificare i token dei peer; `peers/verify` e `peers/revoke`.
- `allowlist`/`blocklist` per nodo (`node_policies`), con `import_only`, `disable_chat` e `disable_search`. Rate limiting e anti-flood al bordo; propagazione delle segnalazioni di moderazione.
- Portabilità: bundle firmati con HMAC e checksum; l'import valida/sanea `MediaUrl` e normalizza `contest_type`; migrazione di festival e identità con `identity_redirects` e audit in `migration_audits`; gli endpoint di migrazione richiedono admin.
- Chat federata: bridge firmato RS256, dedup per `message_id` in `chat_outbox`, ordinamento per `timestamp`; segnalazioni e mute, filtro parole e limite di 10 messaggi/60 s per nodo e utente.
- Eventi: pubblicazione firmata con HMAC (`X-Clakettes-Signature`), SSE con Bearer nell'header (`token` in query deprecato), `since` e `limit` opzionali, replay di 200 e 3 ripetizioni con backoff.
- Resilienza: `/api/federation/resilience/health`, `/heartbeat`, `/metrics` (p50/p95), revoca delle chiavi (`keys/revoke`) e piano incidente in 8 passi. Rotazione/revoca tramite rinnovo del certificato; un nodo compromesso viene invalidato nella directory.
