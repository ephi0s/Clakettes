# Clakettes Schema v1

Erste Version des Föderationsschemas. Definiert die minimalen, zwischen Knoten ausgetauschten Entitäten.

## Entitäten

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status

## Felder und Einschränkungen

- `uuid`: Stabiler globaler Bezeichner (UUID v4).
- `did`: Optionaler dezentraler Bezeichner.
- `handle`: `user@instance`, auflösbar via WebFinger.

## Endpunkte

- `GET /api/federation/manifest`
- `GET /api/federation/directory`
- `GET/POST /api/federation/nodes`
- `POST/GET/PATCH /api/federation/reports`
- `GET /api/federation/.well-known/webfinger`
- `GET/DELETE /api/federation/users/{ref}`

## Anpassbarkeit

- Das Schema ist versioniert; Knoten deklarieren `schema_version` im Manifest.
- Optionale Felder (`did`, `handle`) können weggelassen werden, wenn der Knoten sie nicht unterstützt.
- Datenminimierung (`minimize_data`) erlaubt das Weglassen sensibler Felder im Peering.