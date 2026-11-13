# Esquema Clakettes v1

Primeira versión do esquema de federación. Define as entidades mínimas intercambiadas entre nodos.

## Entidades

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status

## Campos e restricións

- `uuid`: identificador global estable (UUID v4).
- `did`: identificador descentralizado opcional.
- `handle`: `usuario@instancia` resoluble via WebFinger.

## Endpoints

- `GET /api/federation/manifest`
- `GET /api/federation/directory`
- `GET/POST /api/federation/nodes`
- `POST/GET/PATCH /api/federation/reports`
- `GET /api/federation/.well-known/webfinger`
- `GET/DELETE /api/federation/users/{ref}`

## Adecuación

- O esquema é versionado; os nodos declaran `schema_version` no manifest.
- Os campos opcionais (`did`, `handle`) poden omitirse se non son soportados.
- A minimización de datos (`minimize_data`) permite omitir campos sensibles no peering.