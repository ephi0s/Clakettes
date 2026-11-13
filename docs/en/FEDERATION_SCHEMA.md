# Clakettes Schema v1

Initial version of the federation schema. Defines the minimum entities exchanged between nodes.

## Entities

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status

## Fields and restrictions

- `uuid`: stable global identifier (UUID v4).
- `did`: optional decentralized identifier.
- `handle`: `user@instance` resolvable via WebFinger.

## Endpoints

- `GET /api/federation/manifest`
- `GET /api/federation/directory`
- `GET/POST /api/federation/nodes`
- `POST/GET/PATCH /api/federation/reports`
- `GET /api/federation/.well-known/webfinger`
- `GET/DELETE /api/federation/users/{ref}`

## Adjustability

- The schema is versioned; nodes declare `schema_version` in the manifest.
- Optional fields (`did`, `handle`) can be omitted if the node does not support them.
- Data minimization (`minimize_data`) allows omitting sensitive fields in peering.