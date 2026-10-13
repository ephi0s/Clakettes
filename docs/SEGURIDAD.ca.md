# Seguretat — model i checklist

[ES](SEGURIDAD.md) · [EN](SEGURIDAD.en.md) · [FR](SEGURIDAD.fr.md) · [DE](SEGURIDAD.de.md) · [IT](SEGURIDAD.it.md) · [CA](SEGURIDAD.ca.md) · [EU](SEGURIDAD.eu.md) · [GL](SEGURIDAD.gl.md) · [OC](SEGURIDAD.oc.md)

## Tokens i sessions

- Access JWT (HS256, 30 min, `type=access`, `jti` únic) + refresh opac (SHA-256 en BD,
  30 d, rotació en utilitzar). Sessió (`UserSession`) amb IP, dispositiu,
  expiració i revocació; `last_used_at` lazy cada 5 min.
- Purga en arrencada: s'eliminen sessions revocades o caducades fa >30 d.
- Tota validació passa per `validate_access_token` (firma + tipus + sessió
  activa); el WS del xat també. Revocar sessió tanca el WS.
- Passwords amb bcrypt; CalDAV utilitza bearer en URL (redactat en logs).
  Els tokens DAV caduquen als 180 dies (`dav_token_expires_at`, regenerables).

## RGPD

- Privacitat per defecte: `is_public*` en `False` (perfil, email, bio, ubicació).
- Consentiment: `privacy_policy_version` + `privacy_accepted_at` en crear compte.
- Oblit: `DELETE /api/users/me` (i `DELETE /api/users/{id}` admin/organizer)
  anonimitza el compte, esborra sessions/claus/àlies/notificacions/inscripcions
  i desvincula referències; bloqueja esborrar l'últim admin actiu.
- Portabilitat: `GET /api/users/me/export` (JSON amb perfil, rols, inscripcions,
  missatges, sessions, etc.).
- Auditoria (art. 5.2): `audit_logs` append-only amb actor, acció, objectiu i IP
  en esborrats, exportacions, rols/tags i tokens DAV; lectura a
  `GET /api/admin/audit-log` (només admin).
- Pujades: tot fitxer passa per `_save_file` (tipus i màgia validats) i se li
  eliminen metadades identificatives abans de desar: EXIF/XMP en imatges
  (Pillow), tags en MP4/MOV (`ffmpeg -map_metadata -1`, mutagen si no hi ha
  ffmpeg), `/Info` en PDF (pypdf). WebM sense ffmpeg es rebutja (422).

## Autorització

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

## Pagaments

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`). Sense PAN/IBAN en BD: només import, moneda, `provider_ref` i estat.
- Stripe: SDK peresós + verificació de firma (`STRIPE_WEBHOOK_SECRET`).
- Redsys: firma HMAC_SHA256_V1 sense SDK; Bizum amb `pay_methods="z"` (alta prèvia al comerç). Validar contra el sandbox abans de prod.

## Perímetre

- Rate limit SQLite 100/60s per IP (`/dav` 600/60s); `TESTING=true` l'apaga.
- Capçaleres: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`,
  `Content-Security-Policy` estricta a l'API (relaxada només a `/docs`),
  `HSTS` només en producció.
- Cossos ≤10 MB (413). CORS amb credencials i orígens explícits.
- MariaDB en producció exigeix TLS (`?ssl_ca=…` a `DATABASE_URL`).

## Checklist producció

1. `APP_ENV=production`, `SECRET_KEY` de 64 bytes per env (sense ella no arrenca).
2. `CORS_ORIGINS` amb dominis explícits; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS amb proxy + `FORWARDED_ALLOW_IPS`; sense admin `setup` (només es crea fora de prod).
4. Canviar `appUserModelId`/GUID de notificacions Windows si es reanomena l'app.
