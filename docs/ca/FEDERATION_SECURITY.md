# Seguretat federada (Fase 2)

## Model de confiança

- Identitat del node = domini + certificat TLS.
- Peering mutu via mTLS amb certificats de domini (CA pública/privada).
- TLS obligatori entre nodes; validació estricta (sense self-signed en prod).

## Rotació i revocació

- La rotació/revocació es gestiona per renovació del certificat.
- Un node compromès es revoca invalidant el seu certificat i la seva entrada al directori.

## Motivació

Evitar la suplantació de nodes i garantir que només instàncies verificades participin en la federació.

## Ajustos

- `allowlist`/`blocklist` per node (`node_policies`).
- Rate limiting i anti-flood a la vora de la federació.
- Propagació de reportes de moderació entre nodes.