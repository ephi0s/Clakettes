# Seguretat — modèl e checklist

[ES](SEGURIDAD.md) · [EN](SEGURIDAD.en.md) · [FR](SEGURIDAD.fr.md) · [DE](SEGURIDAD.de.md) · [IT](SEGURIDAD.it.md) · [CA](SEGURIDAD.ca.md) · [EU](SEGURIDAD.eu.md) · [GL](SEGURIDAD.gl.md) · [OC](SEGURIDAD.oc.md)

## Tokens e sessions

- Access JWT (HS256, 30 min, `type=access`, `jti` unic) + refresh opac (SHA-256 en BD,
  30 d, rotacion en utilizar). Session (`UserSession`) amb IP, dispositiu,
  expiracion e revocacion; `last_used_at` lazy cada 5 min.
- Purga en aviada: s'escaf fan sessions revocadas o perimidas dempuèi >30 d.
- Tota validacion passa per `validate_access_token` (signatura + tipe + session
  activa); lo WS del chat tanben. Revocar session barra lo WS.
- Senhals amb bcrypt; CalDAV utiliza bearer en URL (redactat en jornaus).
  Los tokens DAV periman a 180 jorns (`dav_token_expires_at`, regenerables).

## RGPD

- Privacitat per defaut: `is_public*` en `False` (perfil, email, bio, ubicacion).
- Consentiment: `privacy_policy_version` + `privacy_accepted_at` en crear compte.
- Oblit: `DELETE /api/users/me` (e `DELETE /api/users/{id}` admin/organizer)
  anonimiza lo compte, escafa sessions/claus/alias/notificacions/inscripcions
  e desliga referéncias; blòca escafar lo darrièr admin actiu.
- Portabilitat: `GET /api/users/me/export` (JSON amb perfil, ròtles, inscripcions,
  messatges, sessions, etc.).
- Auditoria (art. 5.2): `audit_logs` append-only amb actor, accion, objectiu e IP
  en escafaments, exportacions, ròtles/tags e tokens DAV; lectura en
  `GET /api/admin/audit-log` (sonque admin).
- Pujadas: tot fichièr passa per `_save_file` (tipes e magia validats) e se li
  levan metadonadas identificativas abans de gardar: EXIF/XMP en imatges
  (Pillow), tags en MP4/MOV (`ffmpeg -map_metadata -1`, mutagen se i a pas
  ffmpeg), `/Info` en PDF (pypdf). WebM sens ffmpeg se refusa (422).

## Autorizacion

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

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`). Sens PAN/IBAN en BD: sonque import, moneda, `provider_ref` e estat.
- Stripe: SDK peresós + verificacion de signatura (`STRIPE_WEBHOOK_SECRET`).
- Redsys: signatura HMAC_SHA256_V1 sens SDK; Bizum amb `pay_methods="z"` (alta prèvia dins lo comèrci). Validar contra lo sandbox abans de prod.

## Perimètre

- Rate limit SQLite 100/60s per IP (`/dav` 600/60s); `TESTING=true` l'atumba.
- Entèstas: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`,
  `Content-Security-Policy` estricta dins l'API (relassada sonque en `/docs`),
  `HSTS` sonque en produccion.
- Còrses ≤10 MB (413). CORS amb credencials e originhas explicitas.
- MariaDB en produccion exigís TLS (`?ssl_ca=…` en `DATABASE_URL`).

## Checklist produccion

1. `APP_ENV=production`, `SECRET_KEY` de 64 bytes per env (sens ela non avia).
2. `CORS_ORIGINS` amb dominis explicites; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS amb proxy + `FORWARDED_ALLOW_IPS`; sens admin `setup` (sonque se crea fòra de prod).
4. Cambiar `appUserModelId`/GUID de notificacions Windows se se renòmma l'app.
