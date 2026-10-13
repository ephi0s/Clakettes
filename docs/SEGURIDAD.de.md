# Sicherheit — Modell und Checkliste

## Tokens und Sitzungen

- Access-JWT (HS256, 30 Min, `type=access`, eindeutige `jti`) + opaker Refresh (SHA-256 in DB,
  30 T, Rotation bei Verwendung). Sitzung (`UserSession`) mit IP, Gerät,
  Ablauf und Widerruf; `last_used_at` lazy alle 5 Min.
- Purge beim Start: widerrufene oder vor >30 T abgelaufene Sitzungen werden gelöscht.
- Jede Validierung läuft über `validate_access_token` (Signatur + Typ + aktive
  Sitzung); auch das Chat-WS. Sitzungs­widerruf schließt das WS.
- Passwörter mit bcrypt; CalDAV nutzt Bearer in URL (in Logs redigiert).
  DAV-Tokens laufen nach 180 Tagen ab (`dav_token_expires_at`, regenerierbar).

## DSGVO

- Privacy by Default: `is_public*` auf `False` (Profil, E-Mail, Bio, Standort).
- Einwilligung: `privacy_policy_version` + `privacy_accepted_at` bei Kontoerstellung.
- Vergessenwerden: `DELETE /api/users/me` (und `DELETE /api/users/{id}` admin/organizer)
  anonymisiert das Konto, löscht Sitzungen/Schlüssel/Aliase/Benachrichtigungen/Anmeldungen
  und entkoppelt Referenzen; blockiert das Löschen des letzten aktiven Admins.
- Portabilität: `GET /api/users/me/export` (JSON mit Profil, Rollen, Anmeldungen,
  Nachrichten, Sitzungen usw.).
- Audit (Art. 5.2): `audit_logs` append-only mit Akteur, Aktion, Ziel und IP
  bei Löschungen, Exporten, Rollen/Tags und DAV-Tokens; Lesen in
  `GET /api/admin/audit-log` (nur Admin).
- Uploads: jede Datei läuft durch `_save_file` (Typen und Magie validiert) und
  identifizierende Metadaten werden vor dem Speichern entfernt: EXIF/XMP in Bildern
  (Pillow), Tags in MP4/MOV (`ffmpeg -map_metadata -1`, mutagen wenn kein
  ffmpeg), `/Info` in PDF (pypdf). WebM ohne ffmpeg wird abgewiesen (422).

## Autorisierung

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

## Zahlungen

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`). Ohne PAN/IBAN in DB: nur Betrag, Währung, `provider_ref` und Status.
- Stripe: Lazy-SDK + Signaturprüfung (`STRIPE_WEBHOOK_SECRET`).
- Redsys: HMAC_SHA256_V1-Signatur ohne SDK; Bizum mit `pay_methods="z"` (vorherige Freischaltung im Handel). Vor Prod gegen die Sandbox validieren.

## Perimeter

- SQLite-Rate-Limit 100/60s pro IP (`/dav` 600/60s); `TESTING=true` schaltet es ab.
- Header: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`,
  strikte `Content-Security-Policy` in der API (nur in `/docs` gelockert),
  `HSTS` nur in Produktion.
- Bodys ≤10 MB (413). CORS mit Credentials und expliziten Origins.
- MariaDB in Produktion verlangt TLS (`?ssl_ca=…` in `DATABASE_URL`).

## Produktions-Checkliste

1. `APP_ENV=production`, `SECRET_KEY` mit 64 Bytes per Env (ohne sie startet nicht).
2. `CORS_ORIGINS` mit expliziten Domains; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS mit Proxy + `FORWARDED_ALLOW_IPS`; ohne Admin `setup` (wird nur außerhalb von Prod erstellt).
4. `appUserModelId`/GUID der Windows-Benachrichtigungen wechseln wenn die App umbenannt wird.
