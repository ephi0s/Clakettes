# Seguridade — modelo e checklist

[ES](../es/SEGURIDAD.md) · [EN](../en/SEGURIDAD.md) · [FR](../fr/SEGURIDAD.md) · [DE](../de/SEGURIDAD.md) · [IT](../it/SEGURIDAD.md) · [CA](../ca/SEGURIDAD.md) · [EU](../eu/SEGURIDAD.md) · [CA](SEGURIDAD.md) · [OC](../oc/SEGURIDAD.md)

## Tokens e sesións

- Access JWT (HS256, 30 min, `type=access`, `jti` único) + refresh opaco (SHA-256 en BD, 30 d, rotación ao usar). Sesión (`UserSession`) con IP, dispositivo, expiración e revocación; `last_used_at` lazy cada 5 min.
- Purga no arranque: elimínanse sesións revocadas ou caducadas fai >30 d.
- Toda a validación pasa por `validate_access_token` (firma + tipo + sesión activa); o WS do chateo tamén. Revocar unha sesión pecha o WS.
- Contrasinais con bcrypt; CalDAV usa bearer na URL (redactado en logs). Os tokens DAV caducan aos 180 días (`dav_token_expires_at`, regenerables).

## RGPD

- Privacidade por defecto: `is_public*` en `False` (perfil, email, bio, ubicación).
- Consentimento: `privacy_policy_version` + `privacy_accepted_at` ao crear a conta.
- Olvido: `DELETE /api/users/me` (e `DELETE /api/users/{id}` admin/organizer) anonimiza a conta, borra sesións/chaves/alias/notificacións/inscripcions e desvincula referencias; bloquea borrar o último admin activo.
- Portabilidade: `GET /api/users/me/export` (JSON con perfil, roles, inscripcions, mensaxes, sesións, etc.).
- Auditoria (art. 5.2): `audit_logs` append-only con actor, acción, obxectivo e IP en borrados, exportacións, roles/tags e tokens DAV; lectura en `GET /api/admin/audit-log` (solo admin).
- Subidas: todo arquivo pasa por `_save_file` (tipos e maía validados) e elimínanse metadatos identificativos antes de gardar: EXIF/XMP en imaxes (Pillow), etiquetas en MP4/MOV (`ffmpeg -map_metadata -1`, mutagen se non hai ffmpeg), `/Info` en PDF (pypdf). WebM sen ffwxénese rechaza (422).

## Autorización

| Ámbito | Regra |
|--------|-------|
| Festival | `require_festival_admin` (admin global u organizador do festival) |
| Canal | `require_channel_admin` (creador/admin) para xestionar; `require_channel_member` para ler privados |
| Grupo de chat | rol `admin` do grupo para borrar; membro para ler |
| Formulario | `require_form_admin` (creador/admin/organizador) |
| Delegación | delegador ou admin para editar/revocar |
| Roles globais | `is_admin`; auto-join solo con rol `attendee` |
| Roles de canal | `Literal[admin,moderator,member]` (422 fóra da lista) |
| Pagos | doente vía inscripción, admin do festival ou global; webhook mock con `MOCK_WEBHOOK_SECRET` |

## Pagos

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`). Sen PAN/IBAN na BD: só importe, moeda, `provider_ref` e estado.
- Stripe: SDK preguizoso + verificación de firma (`STRIPE_WEBHOOK_SECRET`).
- Redsys: firma HMAC_SHA256_V1 sen SDK; Bizum con `pay_methods="z"` (alta previa no comercio). Validar no sandbox antes de prod.

## Perímetro

- Rate limit SQLite 100/60s por IP (`/dav` 600/60s); `TESTING=true` desactívalo.
- Cabeceras: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy` estrita na API (relaxada só en `/docs`), `HSTS` só en produción.
- Corpos ≤10 MB (413). CORS con credenciais e oríxenes explícitas.
- MariaDB en produción exige TLS (`?ssl_ca=…` en `DATABASE_URL`).

## Checklist produción

1. `APP_ENV=production`, `SECRET_KEY` de 64 bytes por env (sen ella non arranca).
2. `CORS_ORIGINS` con dominios explícitos; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS con proxy + `FORWARDED_ALLOW_IPS`; sen admin `setup` (só créase fóra de prod).
4. Cambiar `appUserModelId`/GUID de notificacións Windows se se renomea a app.

## Federación (fase 2)

- Identidade de nodo = dominio + certificado TLS.
- Peering mutuo vía mTLS con certificados de dominio (CA pública ou privada).
- TLS obrigatorio entre nodos; validación estrita (sen self-signed en prod).
- A rotación/revocación xestionase por renovación do certificado. Un nodo comprometido revócase invalidando o seu certificado e a súa entrada no directorio.
- `allowlist`/`blocklist` por nodo (`node_policies`). Rate limiting e anti-inundación no borde de federación. Propagación de informes de moderación entre nodos.