# Seguranca — model e checklist

[ES](../es/SEGURIDAD.md) · [EN](../en/SEGURIDAD.md) · [FR](../fr/SEGURIDAD.md) · [DE](../de/SEGURIDAD.md) · [IT](../it/SEGURIDAD.md) · [CA](../ca/SEGURIDAD.md) · [EU](../eu/SEGURIDAD.md) · [GL](../gl/SEGURIDAD.md) · [CA](SEGURIDAD.md) · [OC](SEGURIDAD.md)

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
| Rols globals | `is_admin`; auto-join només amb rol `attendee` |
| Rols de canal | `Literal[admin,moderator,member]` (422 fora de la llista) |
| Pagaments | propietari via inscripcio, admin de festival o global; webhook mock amb `MOCK_WEBHOOK_SECRET` |

## Pagaments

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`). Sense PAN/IBAN a la BD: solament import, moneda, `provider_ref` i estat.
- Stripe: SDK perezos + verificacio de signatura (`STRIPE_WEBHOOK_SECRET`).
- Redsys: signatura HMAC_SHA256_V1 sense SDK; Bizum amb `pay_methods="z"` (alta prealable al comerç). Validar contra el sandbox abans de prod.

## Perimetre

- Rate limit SQLite 100/60s per IP (`/dav` 600/60s); `TESTING=true` el desactiva.
- Capçaleres: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy` estricta a l'API (relajada només a `/docs`), `HSTS` solament a produccio.
- Corcos <=10 MB (413). CORS amb credencials i orígens explicitos.
- MariaDB a produccio exigeix TLS (`?ssl_ca=…` a `DATABASE_URL`).

• Llista de comprovacio de productiu

1. `APP_ENV=production`, `SECRET_KEY` de 64 bytes per env (sense ella no arranca).
2. `CORS_ORIGINS` amb dominis explicitos; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS amb proxy + `FORWARDED_ALLOW_IPS`; sense admin `setup` (solament es crea fora de prod).
4. Canvia el `appUserModelId`/GUID de notificacions Windows si es renombra l'aplicacio.

## Federacio (fasa 2)

- Identitat de node = domini + certificat TLS.
- Peering mutue via mTLS amb certificats de domini (CA publica o privada).
- TLS obligatori entre nodes; validacio estricta (sense self-signed a prod).
- La rotacio/revocacio es gestiona per renovacio del certificat. Un node compromes es revoca invalidant el seu certificat i la seva entrada al directori.
- `allowlist`/`blocklist` per node (`node_policies`). Rate limiting i anti-inundada al marge de federacio. Propagacio d'informes de moderacio entre nodes.