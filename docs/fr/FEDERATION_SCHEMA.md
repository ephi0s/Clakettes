# Clakettes Schema v1

Version initiale du schéma de fédération. Définit les entités minimales échangées entre nœuds.

## Entités

- `festival` : id, name, edition, created_at, owner_node
- `user` : id, uuid, did, handle, username, node_origin
- `message` : id, sender, recipient, body, created_at, node_origin
- `moderation_report` : id, reporter_node, target_node, target_user_ref, reason, status

## Champs et restrictions

- `uuid` : identifiant global stable (UUID v4).
- `did` : identifiant décentralisé optionnel.
- `handle` : `user@instance` résoluble via WebFinger.

## Endpoints

- `GET /api/federation/manifest`
- `GET /api/federation/directory`
- `GET/POST /api/federation/nodes`
- `POST/GET/PATCH /api/federation/reports`
- `GET /api/federation/.well-known/webfinger`
- `GET/DELETE /api/federation/users/{ref}`

## Ajustabilité

- Le schéma est versionné ; les nœuds déclarent `schema_version` dans le manifest.
- Les champs optionnels (`did`, `handle`) peuvent être omis si le nœud ne les prend pas en charge.
- La minimisation des données (`minimize_data`) permet d'omettre les champs sensibles dans le peering.