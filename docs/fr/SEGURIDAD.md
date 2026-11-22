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
| Rôles globaux | `require_admin(user, db)` unifié : rôle legacy `admin` (insensible à la casse) ou `UserRole` avec état `ACTIVE`/`APPROVED` ; auto-join seulement avec le rôle `attendee` |
| Alias utilisateur | `require_self_or_admin` (propriétaire ou admin) sur create/update/delete |
| Blocages d'utilisateur | `require_owner_or_admin` (propriétaire ou `can_edit_user`) sur block/unblock/list/status |
| Rôles de canal | `Literal[admin,moderator,member]` (422 hors liste) |
| Paiements | propriétaire via inscription, admin du festival ou global ; webhook mock avec `MOCK_WEBHOOK_SECRET` |

## Paiements

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py` ; `mock` par défaut dans `backend/app/config.py`). Pas de PAN/IBAN en BD : seulement montant, devise, `provider_ref` et statut.
- Stripe : SDK paresseux + vérification de signature (`STRIPE_WEBHOOK_SECRET`).
- Redsys : signature HMAC_SHA256_V1 sans SDK ; Bizum avec `pay_methods="z"` (enregistrement préalable chez le commerçant). Valider dans le sandbox avant la prod.
- `confirm` et `refund` synchronisent `FestivalRegistration.payment_status` (`paid`/`refunded`) et, en paid, `paid_at`/`payment_method`/`transaction_id` ; le `provider` du Payment est pris du provider actif, et non de `PAYMENTS_PROVIDER`.
- **État réel** : Stripe et Redsys ne sont PAS encore opérationnels ; il faut câbler leurs webhooks (`POST /api/payments/webhook/{stripe,redsys}`). Aujourd'hui seul le webhook simulé fonctionne (`POST /api/payments/webhook/mock`).
- Le `confirm` de Redsys renvoie toujours `"pending"` : il ne confirme aucun paiement réel tant que le webhook n'est pas câblé.

## Périmètre

- Rate limit SQLite 100/60 s par IP en global, 600/60 s sur `/dav`, 5/300 s login, 20/60 s refresh et 3/300 s reset et 60/60 s sur la fédération. `TESTING` ∈ {1, true, yes, on} (`app.config.is_testing()`) désactive toutes les limites et l'auto-migration.
- En-têtes : `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy` stricte dans l'API (assouplie seulement sur `/docs`), `HSTS` seulement en production.
- Corps ≤10 Mo (413). CORS avec credentials et origines explicites.
- MariaDB en production exige TLS (`?ssl_ca=…` dans `DATABASE_URL`).

## Checklist production

1. `APP_ENV=production`, `SECRET_KEY` de 64 octets via env (sans elle le démarrage échoue).
2. `CORS_ORIGINS` avec domaines explicites ; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS avec proxy + `FORWARDED_ALLOW_IPS` ; pas d'admin `setup` (seulement créé hors prod).
4. Changer `appUserModelId`/GUID des notifications Windows si l'app est renommée.

## Fédération (phases 2-10)

Détail complet dans [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md). Contrôles en vigueur :

- Identité du nœud = domaine + certificat TLS. Peering mutuel via mTLS avec certificats de domaine (CA publique ou privée) ; TLS obligatoire, pas de self-signed en prod.
- Manifeste signé RSA-SHA256 avec PEM/clé propres et `expires_at` de 24 h ; `whoami` exige un JWT fédéré ; JWKS pour vérifier les tokens des pairs ; `peers/verify` et `peers/revoke`.
- `allowlist`/`blocklist` par nœud (`node_policies`), avec `import_only`, `disable_chat` et `disable_search`. Rate limiting et anti-inondation au bord ; propagation des signalements de modération.
- Portabilité : bundles signés avec HMAC et checksum ; l'import valide/sanitise `MediaUrl` et normalise `contest_type` ; migration des festivals et identités avec `identity_redirects` et audit dans `migration_audits` ; les endpoints de migration exigent admin.
- Chat fédéré : bridge signé RS256, dédup par `message_id` dans `chat_outbox`, tri par `timestamp` ; signalements et mutes, filtre de mots et limite de 10 messages/60 s par nœud et utilisateur.
- Événements : publication signée avec HMAC (`X-Clakettes-Signature`), SSE avec `token` obligatoire en query, `since` et `limit` optionnels, replay de 200 et 3 relances avec backoff.
- Résilience : `/api/federation/resilience/health`, `/heartbeat`, `/metrics` (p50/p95), révocation de clés (`keys/revoke`) et plan d'incident en 8 étapes. Rotation/révocation par renouvellement du certificat ; un nœud compromis est invalidé dans le répertoire.