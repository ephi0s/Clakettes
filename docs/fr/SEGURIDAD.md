# Sécurité — modèle et checklist

[ES](../es/SEGURIDAD.md) · [EN](../en/SEGURIDAD.md) · [FR](SEGURIDAD.md) · [DE](../de/SEGURIDAD.md) · [IT](../it/SEGURIDAD.md) · [CA](../ca/SEGURIDAD.md) · [EU](../eu/SEGURIDAD.md) · [GL](../gl/SEGURIDAD.md) · [OC](../oc/SEGURIDAD.md)

## Tokens et sessions

- Access JWT (HS256, 30 min, `type=access`, `jti` unique) + refresh opaque (SHA-256 en BD, 30 j, rotation à l'utilisation). Session (`UserSession`) avec IP, appareil, expiration et révocation ; `last_used_at` lazy toutes les 5 min.
- Purge au démarrage : sessions révoquées ou expirées depuis >30 j sont supprimées.
- Toute validation passe par `validate_access_token` (signature + type + session active) ; le WS du chat aussi. Révoquer une session ferme le WS.
- Mots de passe avec bcrypt ; CalDAV utilise bearer dans l'URL (redacté dans les logs). Les tokens DAV expirent après 180 jours (`dav_token_expires_at`, renouvelables).

## RGPD

- Vie privée par défaut : `is_public*` en `False` (profil, email, bio, localisation).
- Consentement : `privacy_policy_version` + `privacy_accepted_at` à la création du compte.
- Droit à l'oubli : `DELETE /api/users/me` (et `DELETE /api/users/{id}` admin/organizer) anonymise le compte, supprime sessions/clés/alias/notifications/inscriptions et désactive les références ; bloque la suppression du dernier admin actif.
- Portabilité : `GET /api/users/me/export` (JSON avec profil, rôles, inscriptions, messages, sessions, etc.).
- Audit (art. 5.2) : `audit_logs` append-only avec acteur, action, cible et IP sur suppressions, exportations, rôles/tags et tokens DAV ; lecture à `GET /api/admin/audit-log` (admin uniquement).
- Uploads : tout fichier passe par `_save_file` (types et magie validés) et les métadonnées identifiantes sont supprimées avant enregistrement : EXIF/XMP dans les images (Pillow), tags dans MP4/MOV (`ffmpeg -map_metadata -1`, mutagen si pas de ffmpeg), `/Info` dans PDF (pypdf). WebM sans ffmpeg est rejeté (422).

## Autorisation

| Domaine | Règle |
|---|---|
| Festival | `require_festival_admin` (admin global ou organizer du festival) |
| Canal | `require_channel_admin` (créateur/admin) pour gérer ; `require_channel_member` pour lire les privés |
| Groupe de chat | rôle `admin` du groupe pour supprimer ; membre pour lire |
| Formulaire | `require_form_admin` (créateur/admin/organizer) |
| Délégation | délégateur ou admin pour éditer/révoquer |
| Rôles globaux | `is_admin` ; auto-join seulement avec le rôle `attendee` |
| Rôles de canal | `Literal[admin,moderator,member]` (422 hors liste) |
| Paiements | propriétaire via inscription, admin du festival ou global ; webhook mock avec `MOCK_WEBHOOK_SECRET` |

## Paiements

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`). Pas de PAN/IBAN en BD : seulement montant, devise, `provider_ref` et statut.
- Stripe : SDK paresseux + vérification de signature (`STRIPE_WEBHOOK_SECRET`).
- Redsys : signature HMAC_SHA256_V1 sans SDK ; Bizum avec `pay_methods="z"` (enregistrement préalable chez le commerçant). Valider dans le sandbox avant la prod.

## Périmètre

- Rate limit SQLite 100/60s par IP (`/dav` 600/60s) ; `TESTING=true` le désactive.
- En-têtes : `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy` stricte dans l'API (assouplie seulement sur `/docs`), `HSTS` seulement en production.
- Corps ≤10 Mo (413). CORS avec credentials et origines explicites.
- MariaDB en production exige TLS (`?ssl_ca=…` dans `DATABASE_URL`).

## Checklist production

1. `APP_ENV=production`, `SECRET_KEY` de 64 octets via env (sans elle le démarrage échoue).
2. `CORS_ORIGINS` avec domaines explicites ; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS avec proxy + `FORWARDED_ALLOW_IPS` ; pas d'admin `setup` (seulement créé hors prod).
4. Changer `appUserModelId`/GUID des notifications Windows si l'app est renommée.

## Fédération (phase 2)

- Identité du nœud = domaine + certificat TLS.
- Peering mutuel via mTLS avec certificats de domaine (CA publique ou privée).
- TLS obligatoire entre nœuds ; validation stricte (pas de self-signed en prod).
- La rotation/révocation est gérée par renouvellement du certificat. Un nœud compromis est révoqué en invalidant son certificat et son entrée dans le répertoire.
- `allowlist`/`blocklist` par nœud (`node_policies`). Rate limiting et anti-inondation au bord de la fédération. Propagation des rapports de modération entre nœuds.