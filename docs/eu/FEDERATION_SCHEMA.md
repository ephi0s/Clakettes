# Clakettes Schema v1

Federazioaren lehen bertsioa. Nodoen artean trukatzen diren entitate minimoak definitzen ditu.

## Entitateak

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status

## Eremuak eta murriztapenak

- `uuid`: identifikatzaile global egonkorra (UUID v4).
- `did`: aukerako identifikatzaile deszentralizatua.
- `handle`: `erabiltzailea@instantzia` WebFinger bidez ebazgarria.

## Endpointak

- `GET /api/federation/manifest`
- `GET /api/federation/directory`
- `GET/POST /api/federation/nodes`
- `POST/GET/PATCH /api/federation/reports`
- `GET /api/federation/.well-known/webfinger`
- `GET/DELETE /api/federation/users/{ref}`

## Doigarritasuna

- Eskema bertsionatua da; nodoek `schema_version` deklaratzen dute manifestuan.
- Aukerako eremuak (`did`, `handle`) omite daitezke onartzen ez badira.
- Datu minimizazioak (`minimize_data`) eremu sentikorrak peeringean ometzea ahalbidetzen du.