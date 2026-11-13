# Protocollo di federazione Clakettes (Fase 4)

Passi per creare un server/client interoperabile:

1. Implementare gli endpoint `/api/federation/*`.
2. Esporre il manifest a `/api/federation/manifest` con `schema_version`, `node`, `capabilities`.
3. Registrare il nodo nella directory `/api/federation/directory`.
4. Validare i token dei peer via JWKS (`/api/federation/.well-known/webfinger`).
5. Usare lo schema Clakettes v1 per lo scambio dati.

## Motivazione

Il protocollo permette a nodi indipendenti di scambiare festival, utenti e messaggi senza perdere identità o tracciabilità.

## Adeguatezze

- `consent_required`: richiede consenso esplicito prima di federare i dati di un nodo.
- `import_only`: federazione unidirezionale (solo import, no export).
- `disable_chat`/`disable_search`: permessi per funzione per nodo.
- `minimize_data`: condividere solo il necessario nel peering.