# Clakettes Schema v1

Versión inicial del schema de federación. Define las entidades mínimas intercambiables entre nodos.

## Entidades

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status

## Campos y restricciones

- `uuid`: identificador estable global (UUID v4).
- `did`: identificador descentralizado opcional.
- `handle`: `usuario@instancia` resoluble vía WebFinger.

## Endpoints

- `GET /api/federation/manifest`
- `GET /api/federation/directory`
- `GET/POST /api/federation/nodes`
- `POST/GET/PATCH /api/federation/reports`
- `GET /api/federation/.well-known/webfinger`
- `GET/DELETE /api/federation/users/{ref}`

## Ajustabilidad

- El schema es versionado; los nodos declaran `schema_version` en el manifest.
- Campos opcionales (`did`, `handle`) pueden omitirse si el nodo no los soporta.
- La minimización de datos (`minimize_data`) permite omitir campos sensibles en peering.