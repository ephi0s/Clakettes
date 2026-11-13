# Protocole de fédération Clakettes (Phase 4)

Étapes pour créer un serveur/client interopérable :

1. Implémentez les endpoints `/api/federation/*`.
2. Exposez le manifest à `/api/federation/manifest` avec `schema_version`, `node`, `capabilities`.
3. Enregistrez le nœud dans le répertoire `/api/federation/directory`.
4. Validez les tokens des pairs via JWKS (`/api/federation/.well-known/webfinger`).
5. Utilisez Clakettes Schema v1 pour l'échange de données.

## Motivation

Le protocole permet à des nœuds indépendants d'échanger des festivals, des utilisateurs et des messages sans perdre d'identité ni de traçabilité.

## Réglages

- `consent_required` : exige un consentement explicite avant de fédérer les données d'un nœud.
- `import_only` : fédération unidirectionnelle (import seulement, pas d'export).
- `disable_chat`/`disable_search` : permissions par fonction par nœud.
- `minimize_data` : ne partagez pas plus que nécessaire dans le peering.