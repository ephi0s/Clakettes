# Esquèma Clakettes v1

Primièra version de l'esquèma de federacion. Definís las entitats minimas escambiadas entre nodes.

## Entitats

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status

## Camps e restriccions

- `uuid`: identificant global estable (UUID v4).
- `did`: identificant descentralizat opcional.
- `handle`: `utilizaire@instància` resoluble via WebFinger.

## Endpoints

- `GET /api/federation/manifest`
- `GET /api/federation/directory`
- `GET/POST /api/federation/nodes`
- `POST/GET/PATCH /api/federation/reports`
- `GET /api/federation/.well-known/webfinger`
- `GET/DELETE /api/federation/users/{ref}`

## Ajustabilitat

- L'esquèma es versionat; los nodes declaran `schema_version` dins lo manifest.
- Los camps opcionals (`did`, `handle`) pòdon èsser omeses se non son suportats.
- La minimizacion de las donadas (`minimize_data`) permet d'ometre los camps sensibles dins lo peering.