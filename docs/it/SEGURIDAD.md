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

## Federazione (fasi 2-10)

Dettaglio completo in [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md). Controlli attivi:

- Identità del nodo = dominio + certificato TLS. Peering reciproco via mTLS con certificati di dominio (CA pubblica o privata); TLS obbligatorio, nessun self-signed in prod.
- Manifesto firmato RSA-SHA256 con PEM/chiave propri e `expires_at` di 24 h; `whoami` richiede JWT federato; JWKS per verificare i token dei peer; `peers/verify` e `peers/revoke`.
- `allowlist`/`blocklist` per nodo (`node_policies`), con `import_only`, `disable_chat` e `disable_search`. Rate limiting e anti-flood al bordo; propagazione delle segnalazioni di moderazione.
- Portabilità: bundle firmati con HMAC e checksum; l'import valida/sanea `MediaUrl` e normalizza `contest_type`; migrazione di festival e identità con `identity_redirects` e audit in `migration_audits`; gli endpoint di migrazione richiedono admin.
- Chat federata: bridge firmato RS256, dedup per `message_id` in `chat_outbox`, ordinamento per `timestamp`; segnalazioni e mute, filtro parole e limite di 10 messaggi/60 s per nodo e utente.
- Eventi: pubblicazione firmata con HMAC (`X-Clakettes-Signature`), SSE con `token` obbligatorio in query, `since` e `limit` opzionali, replay di 200 e 3 ripetizioni con backoff.
- Resilienza: `/api/federation/resilience/health`, `/heartbeat`, `/metrics` (p50/p95), revoca delle chiavi (`keys/revoke`) e piano incidente in 8 passi. Rotazione/revoca tramite rinnovo del certificato; un nodo compromesso viene invalidato nella directory.
