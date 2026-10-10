# Seguridad — modelo y checklist

## Tokens y sesiones

- Access JWT (HS256, 30 min, `type=access`) + refresh opaco (SHA-256 en BD,
  30 d, rotación al usar). Sesión (`UserSession`) con IP, dispositivo,
  expiración y revocación; `last_used_at` lazy cada 5 min.
- Toda validación pasa por `validate_access_token` (firma + tipo + sesión
  activa); el WS del chat también. Revocar sesión cierra el WS.
- Passwords con bcrypt; CalDAV usa bearer en URL (redactado en logs).

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

## Perímetro

- Rate limit SQLite 100/60s por IP (`/dav` 600/60s); `TESTING=true` lo apaga.
- Cabeceras: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`.
- Cuerpos ≤10 MB (413). CORS con credenciales y orígenes explícitos.

## Checklist producción

1. `APP_ENV=production`, `SECRET_KEY` de 64 bytes por env (sin ella no arranca).
2. `CORS_ORIGINS` con dominios explícitos; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS con proxy + `FORWARDED_ALLOW_IPS`; sin admin `setup` (solo se crea fuera de prod).
4. Cambiar `appUserModelId`/GUID de notificaciones Windows si se renombra la app.
