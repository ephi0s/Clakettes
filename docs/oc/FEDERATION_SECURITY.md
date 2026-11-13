# Seguretat federada (Fase 2)

## Modèl de fisança

- Identitat del node = domeni + certificat TLS.
- Peering mutu via mTLS amb certificats de domeni (CA publica/privada).
- TLS obligatòri entre nodes; validacion estricta (pas de self-signed en prod).

## Rotacion e revocacion

- La rotacion/revocacion es gerida per renovacion del certificat.
- Un node compromés es revocat en invalidant son certificat e son entrada dins lo repertòri.

## Motivacion

Evitar l'usurpacion de nodes e garantir que solas las instàncias verificadas participen a la federacion.

## Ajustaments

- `allowlist`/`blocklist` per node (`node_policies`).
- Rate limiting e anti-flood al bòrd de la federacion.
- Propagacion dels senhalaments de moderacion entre nodes.