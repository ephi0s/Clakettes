# Seguridad — modelo y checklist

## Tokens y sesiones

- Access JWT (HS256, 30 min, `type=access`, `jti` único) + refresh opaco (SHA-256 en BD,
  30 d, rotación al usar). Sesión (`UserSession`) con IP, dispositivo,
  expiración y revocación; `last_used_at` lazy cada 5 min.
- Purga en arranque: se eliminan sesiones revocadas o caducadas hace >30 d.
- Toda validación pasa por `validate_access_token` (firma + tipo + sesión
  activa); el WS del chat también. Revocar sesión cierra el WS.
- Passwords con bcrypt; CalDAV usa bearer en URL (redactado en logs).
  Los tokens DAV caducan a los 180 días (`dav_token_expires_at`, regenerables).

## RGPD

- Privacidad por defecto: `is_public*` en `False` (perfil, email, bio, ubicación).
- Consentimiento: `privacy_policy_version` + `privacy_accepted_at` al crear cuenta.
- Olvido: `DELETE /api/users/me` (y `DELETE /api/users/{id}` admin/organizer)
  anonimiza la cuenta, borra sesiones/claves/alias/notificaciones/inscripciones
  y desvincula referencias; bloquea borrar el último admin activo.
- Portabilidad: `GET /api/users/me/export` (JSON con perfil, roles, inscripciones,
  mensajes, sesiones, etc.).
- Auditoría (art. 5.2): `audit_logs` append-only con actor, acción, objetivo e IP
  en borrados, exportaciones, roles/tags y tokens DAV; lectura en
  `GET /api/admin/audit-log` (solo admin).
- Subidas: todo fichero pasa por `_save_file` (tipos y magia validados) y se le
  eliminan metadatos identificativos antes de guardar: EXIF/XMP en imágenes
  (Pillow), tags en MP4/MOV (`ffmpeg -map_metadata -1`, mutagen si no hay
  ffmpeg), `/Info` en PDF (pypdf). WebM sin ffmpeg se rechaza (422).

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

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`). Sin PAN/IBAN en BD: solo importe, moneda, `provider_ref` y estado.
- Stripe: SDK perezoso + verificación de firma (`STRIPE_WEBHOOK_SECRET`).
- Redsys: firma HMAC_SHA256_V1 sin SDK; Bizum con `pay_methods="z"` (alta previa en el comercio). Validar contra el sandbox antes de prod.

## Perímetro

- Rate limit SQLite 100/60s por IP (`/dav` 600/60s); `TESTING=true` lo apaga.
- Cabeceras: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`,
  `Content-Security-Policy` estricta en el API (relajada solo en `/docs`),
  `HSTS` solo en producción.
- Cuerpos ≤10 MB (413). CORS con credenciales y orígenes explícitos.
- MariaDB en producción exige TLS (`?ssl_ca=…` en `DATABASE_URL`).

## Checklist producción

1. `APP_ENV=production`, `SECRET_KEY` de 64 bytes por env (sin ella no arranca).
2. `CORS_ORIGINS` con dominios explícitos; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS con proxy + `FORWARDED_ALLOW_IPS`; sin admin `setup` (solo se crea fuera de prod).
4. Cambiar `appUserModelId`/GUID de notificaciones Windows si se renombra la app.
