# Föderierte Sicherheit (Phase 2)

## Vertrauensmodell

- Knotenidentität = Domain + TLS-Zertifikat.
- Gegenseitiges Peering via mTLS mit Domain-Zertifikaten (öffentliche oder private CA).
- TLS obligatorisch zwischen Knoten; strikte Validierung (keine selbstsignierten in Prod).

## Rotation und Widerruf

- Rotation/Widerruf wird durch Zertifikatserneuerung verwaltet.
- Ein kompromittierter Knoten wird widerrufen, indem sein Zertifikat und sein Verzeichniseintrag ungültig gemacht werden.

## Motivation

Vermeidung von Knoten-Identitätsdiebstahl und Sicherstellung, dass nur verifizierte Instanzen an der Föderation teilnehmen.

## Anpassungen

- `allowlist`/`blocklist` pro Knoten (`node_policies`).
- Rate-Limiting und Anti-Flood am Föderationsrand.
- Verbreitung von Moderationsberichten zwischen Knoten.