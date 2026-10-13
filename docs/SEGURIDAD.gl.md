# Seguridade — modelo e checklist

## Tokens e sesións

- Access JWT (HS256, 30 min, `type=access`, `jti` único) + refresh opaco (SHA-256 en BD,
  30 d, rotación ao usar). Sesión (`UserSession`) con IP, dispositivo,
  expiración e revogación; `last_used_at` lazy cada 5 min.
- Purga no arranque: elimínanse sesións revogadas ou caducadas hai >30 d.
- Toda validación pasa por `validate_access_token` (firma + tipo + sesión
  activa); o WS do chat tamén. Revogar sesión pecha o WS.
- Passwords con bcrypt; CalDAV usa bearer en URL (redactado en logs).
  Os tokens DAV caducan aos 180 días (`dav_token_expires_at`, rexenerables).

## RXPD

- Privacidade por defecto: `is_public*` en `False` (perfil, email, bio, localización).
- Consentimento: `privacy_policy_version` + `privacy_accepted_at` ao crear conta.
- Esquecemento: `DELETE /api/users/me` (e `DELETE /api/users/{id}` admin/organizer)
  anonimiza a conta, borra sesións/claves/alias/notificacións/inscricións
  e desvincula referencias; bloquea borrar o último admin activo.
- Portabilidade: `GET /api/users/me/export` (JSON con perfil, roles, inscricións,
  mensaxes, sesións, etc.).
- Auditoría (art. 5.2): `audit_logs` append-only con actor, acción, obxectivo e IP
  en borrados, exportacións, roles/tags e tokens DAV; lectura en
  `GET /api/admin/audit-log` (só admin).
- Subidas: todo ficheiro pasa por `_save_file` (tipos e maxia validados) e elimínaselle
  metadatos identificativos antes de gardar: EXIF/XMP en imaxes
  (Pillow), tags en MP4/MOV (`ffmpeg -map_metadata -1`, mutagen se non hai
  ffmpeg), `/Info` en PDF (pypdf). WebM sen ffmpeg rexéitase (422).

## Autorización

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

## Pagos

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`). Sen PAN/IBAN en BD: só importe, moeda, `provider_ref` e estado.
- Stripe: SDK preguiceiro + verificación de firma (`STRIPE_WEBHOOK_SECRET`).
- Redsys: firma HMAC_SHA256_V1 sen SDK; Bizum con `pay_methods="z"` (alta previa no comercio). Validar contra o sandbox antes de prod.

## Perímetro

- Rate limit SQLite 100/60s por IP (`/dav` 600/60s); `TESTING=true` apágao.
- Cabeceiras: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`,
  `Content-Security-Policy` estrita no API (relaxada só en `/docs`),
  `HSTS` só en produción.
- Corpos ≤10 MB (413). CORS con credenciais e orixes explícitas.
- MariaDB en produción esixe TLS (`?ssl_ca=…` en `DATABASE_URL`).

## Checklist produción

1. `APP_ENV=production`, `SECRET_KEY` de 64 bytes por env (sen ela non arranca).
2. `CORS_ORIGINS` con dominios explícitos; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS con proxy + `FORWARDED_ALLOW_IPS`; sen admin `setup` (só se crea fóra de prod).
4. Cambiar `appUserModelId`/GUID de notificacións Windows se se renomea a app.
