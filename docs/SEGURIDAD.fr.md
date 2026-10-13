# Sécurité — modèle et liste de contrôle

[ES](SEGURIDAD.md) · [EN](SEGURIDAD.en.md) · [FR](SEGURIDAD.fr.md) · [DE](SEGURIDAD.de.md) · [IT](SEGURIDAD.it.md) · [CA](SEGURIDAD.ca.md) · [EU](SEGURIDAD.eu.md) · [GL](SEGURIDAD.gl.md) · [OC](SEGURIDAD.oc.md)

## Tokens et sessions

- Access JWT (HS256, 30 min, `type=access`, `jti` unique) + refresh opaque (SHA-256 en BD,
  30 j, rotation à l'usage). Session (`UserSession`) avec IP, dispositif,
  expiration et révocation ; `last_used_at` lazy chaque 5 min.
- Purge au démarrage : on élimine sessions révoquées ou expirées depuis >30 j.
- Toute validation passe par `validate_access_token` (signature + type + session
  active) ; le WS du chat aussi. Révoquer session ferme le WS.
- Mots de passe avec bcrypt ; CalDAV utilise bearer en URL (caviardé en logs).
  Les tokens DAV expirent à 180 jours (`dav_token_expires_at`, régénérables).

## RGPD

- Confidentialité par défaut : `is_public*` à `False` (profil, email, bio, localisation).
- Consentement : `privacy_policy_version` + `privacy_accepted_at` à la création de compte.
- Oubli : `DELETE /api/users/me` (et `DELETE /api/users/{id}` admin/organizer)
  anonymise le compte, supprime sessions/clés/alias/notifications/inscriptions
  et délie références ; bloque supprimer le dernier admin actif.
- Portabilité : `GET /api/users/me/export` (JSON avec profil, rôles, inscriptions,
  messages, sessions, etc.).
- Audit (art. 5.2) : `audit_logs` append-only avec acteur, action, objectif et IP
  sur suppressions, exportations, rôles/tags et tokens DAV ; lecture sur
  `GET /api/admin/audit-log` (admin uniquement).
- Envois : tout fichier passe par `_save_file` (types et magie validés) et on lui
  élimine métadonnées identificatives avant de garder : EXIF/XMP en images
  (Pillow), tags en MP4/MOV (`ffmpeg -map_metadata -1`, mutagen s'il n'y a pas
  ffmpeg), `/Info` en PDF (pypdf). WebM sans ffmpeg est rejeté (422).

## Autorisation

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

## Paiements

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`). Sans PAN/IBAN en BD : seulement montant, monnaie, `provider_ref` et état.
- Stripe : SDK paresseux + vérification de signature (`STRIPE_WEBHOOK_SECRET`).
- Redsys : signature HMAC_SHA256_V1 sans SDK ; Bizum avec `pay_methods="z"` (haute préalable chez le commerce). Valider contre le sandbox avant prod.

## Périmètre

- Rate limit SQLite 100/60s par IP (`/dav` 600/60s) ; `TESTING=true` l'éteint.
- En-têtes : `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`,
  `Content-Security-Policy` stricte sur l'API (relâchée seulement sur `/docs`),
  `HSTS` seulement en production.
- Corps ≤10 MB (413). CORS avec credentials et origines explicites.
- MariaDB en production exige TLS (`?ssl_ca=…` dans `DATABASE_URL`).

## Liste de contrôle production

1. `APP_ENV=production`, `SECRET_KEY` de 64 bytes par env (sans elle ne démarre pas).
2. `CORS_ORIGINS` avec domaines explicites ; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS avec proxy + `FORWARDED_ALLOW_IPS` ; sans admin `setup` (seulement créé hors prod).
4. Changer `appUserModelId`/GUID de notifications Windows si on renomme l'app.
