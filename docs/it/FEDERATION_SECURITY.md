# Sicurezza federata (Fase 2)

## Modello di fiducia

- Identità del nodo = dominio + certificato TLS.
- Peering reciproco via mTLS con certificati di dominio (CA pubblica/privata).
- TLS obbligatorio tra nodi; validazione rigorosa (no self-signed in prod).

## Rotazione e revoca

- La rotazione/revoca è gestita dal rinnovo del certificato.
- Un nodo compromesso è revocato invalidando il suo certificato e la sua voce nella directory.

## Motivazione

Evitare l'impersonazione dei nodi e garantire che solo istanze verificate partecipino alla federazione.

## Adeguatezze

- `allowlist`/`blocklist` per nodo (`node_policies`).
- Rate limiting e anti-flood al bordo della federazione.
- Propagazione dei segnalazioni di moderazione tra nodi.