# Seguridade federada (Fase 2)

## Modelo de confianza

- Identidade do nodo = dominio + certificado TLS.
- Peering mutuo via mTLS con certificados de dominio (CA pública/privada).
- TLS obrigatoria entre nodos; validación estrita (sen self-signed en prod).

## Rotación e revogación

- A rotación/revogación xestiónase pola renovación do certificado.
- Un nodo comprometido revógase invalidando o seu certificado e a súa entrada no directorio.

## Motivación

Evitar a suplantación de nodos e garantir que só instancias verificadas participen na federación.

## Adecuacións

- `allowlist`/`blocklist` por nodo (`node_policies`).
- Rate limiting e anti-flood no bordo da federación.
- Propagación de reportes de moderación entre nodos.