# Clakettes federation protocol (Phase 4)

Steps to create an interoperable server/client:

1. Implement the `/api/federation/*` endpoints.
2. Expose the manifest at `/api/federation/manifest` with `schema_version`, `node`, `capabilities`.
3. Register the node in the directory `/api/federation/directory`.
4. Validate peer tokens via JWKS (`/api/federation/.well-known/webfinger`).
5. Use Clakettes Schema v1 for data exchange.

## Motivation

The protocol allows independent nodes to exchange festivals, users and messages without losing identity or traceability.

## Adjustments

- `consent_required`: requires explicit consent before federating a node's data.
- `import_only`: unidirectional federation (import only, no export).
- `disable_chat`/`disable_search`: per-function permissions per node.
- `minimize_data`: do not share more than necessary in peering.