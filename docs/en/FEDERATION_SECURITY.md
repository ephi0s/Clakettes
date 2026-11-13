# Federated security (Phase 2)

## Trust model

- Node identity = domain + TLS certificate.
- Mutual peering via mTLS with domain certificates (public or private CA).
- TLS mandatory between nodes; strict validation (no self-signed in prod).

## Rotation and revocation

- Rotation/revocation is managed by certificate renewal.
- A compromised node is revoked by invalidating its certificate and its directory entry.

## Motivation

Prevent node impersonation and ensure that only verified instances participate in federation.

## Adjustments

- `allowlist`/`blocklist` per node (`node_policies`).
- Rate limiting and anti-flood at federation edge.
- Moderation report propagation between nodes.