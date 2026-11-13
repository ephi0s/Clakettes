# Schema Clakettes v1

Prima versione dello schema di federazione. Definisce le entità minime scambiate tra nodi.

## Entità

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status

## Campi e vincoli

- `uuid`: identificatore globale stabile (UUID v4).
- `did`: identificatore decentralizzato opzionale.
- `handle`: `utente@istanza` risolvibile via WebFinger.

## Endpoint

- `GET /api/federation/manifest`
- `GET /api/federation/directory`
- `GET/POST /api/federation/nodes`
- `POST/GET/PATCH /api/federation/reports`
- `GET /api/federation/.well-known/webfinger`
- `GET/DELETE /api/federation/users/{ref}`

## Adeguatezza

- Lo schema è versionato; i nodi dichiarano `schema_version` nel manifest.
- I campi opzionali (`did`, `handle`) possono essere omessi se non supportati.
- La minimizzazione dei dati (`minimize_data`) consente di omettere campi sensibili nel peering.