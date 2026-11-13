# Sécurité fédérée (Phase 2)

## Modèle de confiance

- Identité du nœud = domaine + certificat TLS.
- Peering mutuel via mTLS avec certificats de domaine (CA publique ou privée).
- TLS obligatoire entre nœuds ; validation stricte (pas de self-signed en prod).

## Rotation et révocation

- La rotation/révocation est gérée par le renouvellement du certificat.
- Un nœud compromis est révoqué en invalidant son certificat et son entrée dans le répertoire.

## Motivation

Éviter l'usurpation d'identité des nœuds et garantir que seules les instances vérifiées participent à la fédération.

## Réglages

- `allowlist`/`blocklist` par nœud (`node_policies`).
- Rate limiting et anti-inondation au bord de la fédération.
- Propagation des rapports de modération entre nœuds.