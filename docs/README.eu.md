# Dokumentazioa — Clakettes

Dokumentazio osoa plataformaren 9 hizkuntzetan dago. Gaztelania kanonikoa da:
[Español](README.md) · [English](README.en.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Italiano](README.it.md) · [Català](README.ca.md) · [Galego](README.gl.md) · [Occitan](README.oc.md).

Indize hau proiektuaren dokumentazioaren sarrera nagusia da. Erabiltzaile, administratzaile edo garatzaile batek gida zuzena aurkitzeko pentsatuta dago ausazko fitxategiak irakurri gabe.

## Nola nabigatu dokumentazioan

- **App-a erabili nahi dut** → [USO.md](USO.eu.md) + [FUNCIONAL.md](FUNCIONAL.eu.md)
- **Hedapen bat administratzen dut** → [ADMINISTRACION.md](ADMINISTRACION.eu.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.eu.md) + [SEGURIDAD.md](SEGURIDAD.eu.md)
- **Garapena** → [ARQUITECTURA.md](ARQUITECTURA.eu.md) + [DESARROLLO.md](DESARROLLO.eu.md) + [API.md](API.md) + [DATABASE.md](DATABASE.eu.md)
- **IA / agentea** → [ARQUITECTURA.md](ARQUITECTURA.eu.md) eta zereginaren dokumentua; nahitaezko komando eta konbentzioak [../AGENTS.md](../AGENTS.md)-n daude

## Dokumentazioaren printzipioak

- **Gai bakoitzeko dokumentu kanoniko bakarra**: [SEGURIDAD.md](SEGURIDAD.eu.md), [USO.md](USO.eu.md), [DATABASE.md](DATABASE.eu.md) eta [API.md](API.md) dira beren esparruko erreferentzia ofiziala.
- **Audientziako dokumentazioa**: gida bakoitza irakurle-mota baterako idatzita dago, ez komando-multzo bakar baterako.
- **Esteka zuzenak**: hemendik klik bat baino gutxiagotan irits daiteke eduki garrantzitsura.
- **Beharrezko bikoizketarik gabe**: bigarren mailako dokumentuek kanonikora estekatzen dute errepikatu beharrean.

## Indizea dokumentuka

| Documento | Qué cubre | Audiencia |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.eu.md) | Utilidad real por rol y flujos (festival, inscripción, comités, premios, chat/E2EE) | usuario, admin, IA |
| [USO.md](USO.eu.md) | Arranque, variables, migración SQLite↔MariaDB, backups, roles y operación | usuario, admin |
| [ADMINISTRACION.md](ADMINISTRACION.eu.md) | Endpoints `/api/admin`, cuenta inicial, rotación de secretos, límites, troubleshooting | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.eu.md) | Perfiles Docker, puertos, volúmenes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.eu.md) | Tokens, matriz `require_*`, perímetro, checklist producción | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.eu.md) | Mapa sistema + reglas backend/frontend + flujos clave | dev, IA |
| [API.md](API.md) | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.md](DESARROLLO.eu.md) | Convención para añadir endpoint/pantalla + puertas CI | dev, IA |
| [HERRAMIENTAS.md](HERRAMIENTAS.eu.md) | Scripts `start.*`, builds distribuibles, Docker, fixes CI | dev |
| [PUSH.md](PUSH.eu.md) | Decisión de notificaciones sin Firebase | dev |
| [DATABASE.md](DATABASE.eu.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| [BACKEND.md](BACKEND.eu.md) | Guía del backend (capas, config, auth, tests) | dev |
| [AUDITORIA.md](AUDITORIA.eu.md) | Informe de auditoría (rev. 10/10/2026) | referencia |

## Ibilbide gomendatua profilez

### Azken erabiltzailea

1. [USO.md](USO.eu.md)
2. [FUNCIONAL.md](FUNCIONAL.eu.md)
3. [SEGURIDAD.md](SEGURIDAD.eu.md) baimenak edo ingurune produktiboa berrikusi behar badituzte soilik

### Hedapen-administratzailea

1. [ADMINISTRACION.md](ADMINISTRACION.eu.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.eu.md)
3. [SEGURIDAD.md](SEGURIDAD.eu.md)
4. [USO.md](USO.eu.md)

### Garatzailea

1. [../AGENTS.md](../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.eu.md)
3. [DESARROLLO.md](DESARROLLO.eu.md)
4. [API.md](API.md)
5. [DATABASE.md](DATABASE.eu.md)

## Dokumentazioa mantentzeko konbentzioak

- Eguneratu dokumentu kanonikoa edozein laburpen edo indize baino lehen.
- Abiarazte-fluxu bat aldatzen baduzu, sinkronizatu [README.md](../README.eu.md), [USO.md](USO.eu.md) eta [HERRAMIENTAS.md](HERRAMIENTAS.eu.md).
- API publiko bat aldatzen baduzu, eguneratu [API.md](API.md) eta, dagokionean, [DESARROLLO.md](DESARROLLO.eu.md).
- Eskema edo iraunkortasuna aldatzen baduzu, berrikusi [DATABASE.md](DATABASE.eu.md) eta migrazioak.

## FAQ azkarra

- **Nondik hasi?** Irakurri [USO.md](USO.eu.md) app-a operatuko baduzu; irakurri [ARQUITECTURA.md](ARQUITECTURA.eu.md) garatuko baduzu.
- **Zer da kanonikoa eta zer ez?** [USO.md](USO.eu.md), [SEGURIDAD.md](SEGURIDAD.eu.md), [API.md](API.md) eta [DATABASE.md](DATABASE.eu.md) dira gai horietarako erreferentzia ofiziala.
- **Non aurkitzen dut komando edo script bat?** Berrikusi [HERRAMIENTAS.md](HERRAMIENTAS.eu.md) eta [../README.md](../README.eu.md).
- **Nola jakin aldaketa batek dokumentazioa behar duen?** Abiarazte, baimen, azpiegitura, API edo datu-ereduan eragiten badu, dagokion dokumentazioan islatu behar da.

## Ikusi halaber

- [../README.md](../README.eu.md): proiektuaren ikuspegi orokorra
- [USO.md](USO.eu.md): operazioa eta tokiko konfigurazioa
- [ADMINISTRACION.md](ADMINISTRACION.eu.md): hedapen- eta administrazio-esparrua
- [ARQUITECTURA.md](ARQUITECTURA.eu.md): sistemaren mapa teknikoa
- [API.md](API.md): endpoint-en erreferentzia

## Gomendatutako hasiera

Tokiko ingurune batean hasteko:

```bash
cd backend && python -m uvicorn app.main:app --reload
cd frontend && flutter run
```

Edo, proiektuaren script-ak erabiliz:

```bat
start.bat --dev
```

Proiektuaren komando eta profilen erreferentzia osoa [HERRAMIENTAS.md](HERRAMIENTAS.eu.md)-n eta [../README.md](../README.eu.md)-n dago.
