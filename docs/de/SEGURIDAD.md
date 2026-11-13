# Sicherheit — Modell und Checkliste

[ES](../es/SEGURIDAD.md) · [EN](../en/SEGURIDAD.md) · [FR](../fr/SEGURIDAD.md) · [DE](SEGURIDAD.md) · [IT](../it/SEGURIDAD.md) · [CA](../ca/SEGURIDAD.md) · [EU](../eu/SEGURIDAD.md) · [GL](../gl/SEGURIDAD.md) · [OC](../oc/SEGURIDAD.md)

## Tokens und Sitzungen

- Access JWT (HS256, 30 min, `type=access`, eindeutiges `jti`) + opaker Refresh (SHA-256 in DB, 30 Tage, Rotation bei Nutzung). Sitzung (`UserSession`) mit IP, Gerät, Ablauf und Widerruf; `last_used_at` lazy alle 5 Min.
- Bereinigung beim Start: widerrufene oder abgelaufene Sitzungen älter als 30 Tage werden gelöscht.
- Alle Validierung läuft über `validate_access_token` (Signatur + Typ + aktive Sitzung); der Chat-WS ebenfalls. Widerruf einer Sitzung schließt den WS.
- Passwörter mit bcrypt; CalDAV verwendet Bearer in URL (redacted in Logs). DAV-Tokens laufen nach 180 Tagen ab (`dav_token_expires_at`, verlängerbar).

## Datenschutz (DSGVO)

- Datenschutz nach Voreinstellung: `is_public*` auf `False` (Profil, E-Mail, Bio, Standort).
- Einwilligung: `privacy_policy_version` + `privacy_accepted_at` bei Kontoerstellung.
- Recht auf Vergessenwerden: `DELETE /api/users/me` (und `DELETE /api/users/{id}` admin/organizer) anonymisiert das Konto, löscht Sitzungen/Schlüssel/Alias/Benachrichtigungen/Anmeldungen und entkoppelt Verweise; blockiert Löschung des letzten aktiven Admin.
- Datenübertragbarkeit: `GET /api/users/me/export` (JSON mit Profil, Rollen, Anmeldungen, Nachrichten, Sitzungen usw.).
- Audit (Art. 5.2): `audit_logs` append-only mit Akteur, Aktion, Ziel und IP bei Löschungen, Exporten, Rollen/Tags und DAV-Tokens; Lesen unter `GET /api/admin/audit-log` (nur Admin).
- Uploads: jede Datei durchläuft `_save_file` (Typen und Magie validiert) und identifizierende Metadaten werden vor dem Speichern entfernt: EXIF/XMP in Bildern (Pillow), Tags in MP4/MOV (`ffmpeg -map_metadata -1`, mutagen wenn kein ffmpeg), `/Info` in PDF (pypdf). WebM ohne ffmpeg wird abgelehnt (422).

## Autorisierung

| Bereich | Regel |
|---------|-------|
| Festival | `require_festival_admin` (globaler Admin oder Festival-Organizer) |
| Kanal | `require_channel_admin` (Ersteller/Admin) zum Verwalten; `require_channel_member` zum Lesen privater |
| Chat-Gruppe | Rolle `admin` der Gruppe zum Löschen; Mitglied zum Lesen |
| Formular | `require_form_admin` (Ersteller/Admin/Organizer) |
| Delegation | Delegierender oder Admin zum Bearbeiten/Widerrufen |
| Globale Rollen | `is_admin`; Auto-Join nur mit Rolle `attendee` |
| Kanalrollen | `Literal[admin,moderator,member]` (422 außerhalb der Liste) |
| Zahlungen | Eigentümer über Anmeldung, Festival-Admin oder globaler Admin; Mock-Webhook mit `MOCK_WEBHOOK_SECRET` |

## Zahlungen

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`). Keine PAN/IBAN in DB: nur Betrag, Währung, `provider_ref` und Status.
- Stripe: Lazy-SDK + Signaturverifizierung (`STRIPE_WEBHOOK_SECRET`).
- Redsys: HMAC_SHA256_V1-Signatur ohne SDK; Bizum mit `pay_methods="z"` (vorherige Händlerregistrierung). Gegen Sandbox vor Prod validieren.

## Perimeter

- Rate-Limit SQLite 100/60s pro IP (`/dav` 600/60s); `TESTING=true` schaltet es aus.
- Header: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`, strenge `Content-Security-Policy` in der API (entspannt nur auf `/docs`), `HSTS` nur in Produktion.
- Körper ≤10 MB (413). CORS mit Credentials und expliziten Ursprüngen.
- MariaDB in Produktion erfordert TLS (`?ssl_ca=…` in `DATABASE_URL`).

## Produktions-Checkliste

1. `APP_ENV=production`, `SECRET_KEY` von 64 Bytes via Env (ohne sie startet es nicht).
2. `CORS_ORIGINS` mit expliziten Domains; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS mit Proxy + `FORWARDED_ALLOW_IPS`; kein Admin `setup` (nur außerhalb von Prod erstellt).
4. `appUserModelId`/GUID der Windows-Benachrichtigungen ändern, wenn App umbenannt wird.

## Föderation (Phase 2)

- Knotenidentität = Domain + TLS-Zertifikat.
- Gegenseitiges Peering via mTLS mit Domain-Zertifikaten (öffentliche oder private CA).
- TLS obligatorisch zwischen Knoten; strikte Validierung (keine selbstsignierten in Prod).
- Rotation/Widerruf wird durch Zertifikatserneuerung verwaltet. Ein kompromittierter Knoten wird widerrufen durch Invalidierung seines Zertifikats und seines Verzeichniseintrags.
- `allowlist`/`blocklist` pro Knoten (`node_policies`). Rate-Limiting und Anti-Flood am Föderationsrand. Verbreitung von Moderationsberichten zwischen Knoten.