# Sicurezza — modello e checklist

[ES](SEGURIDAD.md) · [EN](SEGURIDAD.en.md) · [FR](SEGURIDAD.fr.md) · [DE](SEGURIDAD.de.md) · [IT](SEGURIDAD.it.md) · [CA](SEGURIDAD.ca.md) · [EU](SEGURIDAD.eu.md) · [GL](SEGURIDAD.gl.md) · [OC](SEGURIDAD.oc.md)

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
| Roles globales | `is_admin`; auto-join solo con rol `attendee` |
| Roles de canal | `Literal[admin,moderator,member]` (422 fuera de lista) |
| Pagos | dueño vía inscripción, admin de festival o global; webhook mock con `MOCK_WEBHOOK_SECRET` |

## Pagamenti

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`). Senza PAN/IBAN nel DB: solo importo, valuta, `provider_ref` e stato.
- Stripe: SDK pigro + verifica della firma (`STRIPE_WEBHOOK_SECRET`).
- Redsys: firma HMAC_SHA256_V1 senza SDK; Bizum con `pay_methods="z"` (attivazione previa nel commercio). Validare contro il sandbox prima di prod.

## Perimetro

- Rate limit SQLite 100/60s per IP (`/dav` 600/60s); `TESTING=true` lo spegne.
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
