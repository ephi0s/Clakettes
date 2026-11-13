# Clakettes Föderationsprotokoll (Phase 4)

Schritte zur Erstellung eines interoperablen Server/Client:

1. Die Endpunkte `/api/federation/*` implementieren.
2. Das Manifest unter `/api/federation/manifest` mit `schema_version`, `node`, `capabilities` bereitstellen.
3. Den Knoten im Verzeichnis `/api/federation/directory` registrieren.
4. Peer-Tokens über JWKS validieren (`/api/federation/.well-known/webfinger`).
5. Clakettes Schema v1 für den Datenaustausch verwenden.

## Motivation

Das Protokoll erlaubt es unabhängigen Knoten, Festivals, Nutzer und Nachrichten auszutauschen, ohne Identität oder Nachvollziehbarkeit zu verlieren.

## Anpassungen

- `consent_required`: Erfordert ausdrückliche Zustimmung, bevor die Daten eines Knoten fédérés werden.
- `import_only`: Einseitige Föderation (nur Import, kein Export).
- `disable_chat`/`disable_search`: Berechtigungen pro Funktion pro Knoten.
- `minimize_data`: Nicht mehr als nötig im Peering teilen.