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
| Globale Rollen | `require_admin(user, db)` vereinheitlicht: Legacy-Rolle `admin` (case-insensitive) oder `UserRole` mit Status `ACTIVE`/`APPROVED`; Auto-Join nur mit Rolle `attendee` |
| Nutzer-Aliase | `require_self_or_admin` (Eigentümer oder Admin) bei create/update/delete |
| Nutzer-Blockierungen | `require_owner_or_admin` (Eigentümer oder `can_edit_user`) bei block/unblock/list/status |
| Kanalrollen | `Literal[admin,moderator,member]` (422 außerhalb der Liste) |
| Zahlungen | Eigentümer über Anmeldung, Festival-Admin oder globaler Admin; Mock-Webhook mit `MOCK_WEBHOOK_SECRET` |

## Zahlungen

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`; `mock` als Standard in `backend/app/config.py`). Keine PAN/IBAN in DB: nur Betrag, Währung, `provider_ref` und Status.
- Stripe: Lazy-SDK + Signaturverifizierung (`STRIPE_WEBHOOK_SECRET`).
- Redsys: HMAC_SHA256_V1-Signatur ohne SDK; Bizum mit `pay_methods="z"` (vorherige Händlerregistrierung). Gegen Sandbox vor Prod validieren.
- `confirm` und `refund` synchronisieren `FestivalRegistration.payment_status` (`paid`/`refunded`) und bei paid `paid_at`/`payment_method`/`transaction_id`; der `provider` des Payment wird vom aktiven Provider übernommen, nicht von `PAYMENTS_PROVIDER`.
- **Aktueller Status**: Stripe und Redsys sind noch NICHT betriebsbereit; ihre Webhooks müssen noch verdrahtet werden (`POST /api/payments/webhook/{stripe,redsys}`). Derzeit funktioniert nur der simulierte Webhook (`POST /api/payments/webhook/mock`).
- Das `confirm` von Redsys gibt immer `"pending"` zurück: es bestätigt keine echten Zahlungen, bis der Webhook verdrahtet ist.

## Perimeter

- SQLite-Rate-Limit 100/60 s global pro IP, 600/60 s in `/dav`, 5/300 s Login, 20/60 s Refresh und 3/300 s Reset und 60/60 s in der Föderation. `TESTING` ∈ {1, true, yes, on} (`app.config.is_testing()`) schaltet alle Limits und die Auto-Migration ab.
- Header: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`, strenge `Content-Security-Policy` in der API (entspannt nur auf `/docs`), `HSTS` nur in Produktion.
- Körper ≤10 MB (413). CORS mit Credentials und expliziten Ursprüngen.
- MariaDB in Produktion erfordert TLS (`?ssl_ca=…` in `DATABASE_URL`).

## Produktions-Checkliste

1. `APP_ENV=production`, `SECRET_KEY` von 64 Bytes via Env (ohne sie startet es nicht).
2. `CORS_ORIGINS` mit expliziten Domains; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS mit Proxy + `FORWARDED_ALLOW_IPS`; kein Admin `setup` (nur außerhalb von Prod erstellt).
4. `appUserModelId`/GUID der Windows-Benachrichtigungen ändern, wenn App umbenannt wird.

## Härtung und Lieferkette (11/2026)

- **Abhängigkeits-Audit**: `tools/audit_deps.py` fragt OSV (CVE/GHSA) für `requirements`, `pubspec.lock` und ein venv ab. Bsp.: `python tools/audit_deps.py --requirements backend/requirements.txt --requirements backend/requirements-dev.txt --lock frontend/pubspec.lock --venv backend/.venv --fail-on fixable`. Bei der Prüfung trat eine nicht behebbare Warnung zu python-ecdsa (CVE-2024-23342) nur in der lokalen `.venv` auf; `pip show` bestätigt, dass kein Paket es erfordert und eine saubere Auflösung der requirements es nicht installiert – es gehört daher nicht zum Projekt.
- **Fixierte/gepatchte Versionen**: `httpx2>=2.12.0`, `httpcore2>=2.10.0`, `pyasn1>=0.6.5`, `bcrypt==5.0.0`, `pytest==9.2.0`, `icalendar==7.3.2`. Die direkten Versionen waren bei der Prüfung bereits frei von OSV-Hinweisen.
- **Produktion**: `docker compose --profile prod` erfordert `APP_ENV=production`, `SECRET_KEY`, explizites `CORS_ORIGINS`, `PUBLIC_BASE_URL` und `DATABASE_URL` mit TLS-Parametern; die Startvalidierung blockiert schwache/Platzhalter-Schlüssel. `start.ps1` erzeugt einen zufälligen Schlüssel, wenn `SECRET_KEY` fehlt (vorher wurde ein bekannter gesetzt).
- **Backend**: Middleware und Sicherheitsvalidierung von `app/main.py` nach `app/security.py` verschoben; CORS beschränkt Header; docs/redoc/openapi in Produktion deaktiviert; Portabilitätsexport erfordert verifizierten Benutzer/Admin/föderierten Knoten; Knotenregistrierung erfordert Authentifizierung in Produktion; föderiertes JWKS wird nur von registrierten Knoten geladen (Anti-SSRF, keine Redirects); SSE akzeptiert Bearer im Header (Query-`token` veraltet); Mock-Webhooks mit `compare_digest`; Passwörter >72 Bytes werden mit 422 abgelehnt; Bundle-Import übernimmt nur Profilfelder (nie `role`/`is_active`/Privatsphäre); SVG mit CSP-Sandbox ausgeliefert.
- **Frontend**: Tokens und E2EE-Schlüssel in `flutter_secure_storage` mit einmaliger Migration (Web nutzt SharedPreferences); einzelner Helper `UrlLauncherService` mit Allowlist `http`/`https`/`mailto`/`tel`/`geo`; HTTPS-Validierung des Backends außer für lokale Dev-Hosts; Logout leert Hive-Boxen und den Socket; CSP in `web/index.html` und HSTS/nosniff in `nginx.conf`.
- **Referenzen**: OWASP Top 10 2025 (A02 Konfiguration, A03 Lieferkette, A05 Injektion, A07 Authentifizierung) und OWASP MASVS für Flutter.

## Föderation (Phasen 2-10)

Vollständige Details in [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md). Geltende Kontrollen:

- Knotenidentität = Domain + TLS-Zertifikat. Gegenseitiges Peering via mTLS mit Domain-Zertifikaten (öffentliche oder private CA); TLS obligatorisch, keine selbstsignierten in Prod.
- RSA-SHA256-signiertes Manifest mit eigenem PEM/Schlüssel und `expires_at` von 24 h; `whoami` erfordert föderiertes JWT; JWKS zur Verifikation von Peer-Tokens; `peers/verify` und `peers/revoke`.
- `allowlist`/`blocklist` pro Knoten (`node_policies`), mit `import_only`, `disable_chat` und `disable_search`. Rate-Limiting und Anti-Flood am Rand; Verbreitung von Moderationsberichten.
- Portabilität: HMAC-signierte Bundles mit Checksum; der Import validiert/saniert `MediaUrl` und normalisiert `contest_type`; Migration von Festivals und Identitäten mit `identity_redirects` und Audit in `migration_audits`; die Migrations-Endpoints erfordern Admin.
- Föderierter Chat: RS256-signierte Bridge, Deduplizierung nach `message_id` in `chat_outbox`, Sortierung nach `timestamp`; Meldungen und Mutes, Wortfilter und Limit von 10 Nachrichten/60 s pro Knoten und Nutzer.
- Ereignisse: HMAC-signiertes Publishing (`X-Clakettes-Signature`), SSE mit Bearer im Header (`token` in der Query veraltet), `since` und `limit` optional, Replay von 200 und 3 Wiederholungen mit Backoff.
- Resilienz: `/api/federation/resilience/health`, `/heartbeat`, `/metrics` (p50/p95), Schlüssel-Widerruf (`keys/revoke`) und Incident-Plan in 8 Schritten. Rotation/Widerruf durch Zertifikatserneuerung; ein kompromittierter Knoten wird im Verzeichnis invalidiert.