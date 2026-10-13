# Segurtasuna — eredua eta checklist-a

[ES](SEGURIDAD.md) · [EN](SEGURIDAD.en.md) · [FR](SEGURIDAD.fr.md) · [DE](SEGURIDAD.de.md) · [IT](SEGURIDAD.it.md) · [CA](SEGURIDAD.ca.md) · [EU](SEGURIDAD.eu.md) · [GL](SEGURIDAD.gl.md) · [OC](SEGURIDAD.oc.md)

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
| Roles globales | `is_admin`; auto-join solo con rol `attendee` |
| Roles de canal | `Literal[admin,moderator,member]` (422 fuera de lista) |
| Pagos | dueño vía inscripción, admin de festival o global; webhook mock con `MOCK_WEBHOOK_SECRET` |

## Ordainketak

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`). PAN/IBAN gabe BDn: zenbatekoa, moneta, `provider_ref` eta egoera soilik.
- Stripe: SDK nagia + sinadura-egiaztapena (`STRIPE_WEBHOOK_SECRET`).
- Redsys: HMAC_SHA256_V1 sinadura SDK gabe; Bizum `pay_methods="z"`-rekin (alta aurretik merkataritzan). Sandbox-aren aurka balidatu prod aurretik.

## Perimetroa

- Rate limit SQLite 100/60s IP-ko (`/dav` 600/60s); `TESTING=true`-k itzali egiten du.
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
