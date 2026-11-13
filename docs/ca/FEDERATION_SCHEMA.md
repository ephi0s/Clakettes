# Esquema Clakettes v1

Primera versió de l'esquema de federació. Defineix les entitats mínimes intercanviades entre nodes.

## Entitats

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status

## Camps i restriccions

- `uuid`: identificador global estable (UUID v4).
- `did`: identificador descentralitzat opcional.
- `handle`: `usuari@instancia` resoluble via WebFinger.

## Endpoints

- `GET /api/federation/manifest`
- `GET /api/federation/directory`
- `GET/POST /api/federation/nodes`
- `POST/GET/PATCH /api/federation/reports`
- `GET /api/federation/.well-known/webfinger`
- `GET/DELETE /api/federation/users/{ref}`

## Ajustabilitat

- L'esquema és versionat; els nodes declaren `schema_version` al manifest.
- Els camps opcionals (`did`, `handle`) poden omitir-se si no són suportats.
- La minimització de dades (`minimize_data`) permet ometre camps sensibles en el peering.