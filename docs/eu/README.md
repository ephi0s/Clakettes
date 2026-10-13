# Dokumentazioa — Clakettes

Dokumentazio osoa plataformaren 9 hizkuntzetan dago. Gaztelania kanonikoa da:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

Indize hau proiektuaren dokumentazioaren sarrera nagusia da. Erabiltzaile, administratzaile edo garatzaile batek gida zuzena aurkitzeko pentsatuta dago ausazko fitxategiak irakurri gabe.

## Nola nabigatu dokumentazioan

- **App-a erabili nahi dut** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Hedapen bat administratzen dut** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Garapena** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](../es/API.md) + [DATABASE.md](DATABASE.md)
- **IA / agentea** → [ARQUITECTURA.md](ARQUITECTURA.md) eta zereginaren dokumentua; nahitaezko komando eta konbentzioak [../AGENTS.md](../../AGENTS.md)-n daude

## Dokumentazioaren printzipioak

- **Gai bakoitzeko dokumentu kanoniko bakarra**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) eta [API.md](../es/API.md) dira beren esparruko erreferentzia ofiziala.
- **Audientziako dokumentazioa**: gida bakoitza irakurle-mota baterako idatzita dago, ez komando-multzo bakar baterako.
- **Esteka zuzenak**: hemendik klik bat baino gutxiagotan irits daiteke eduki garrantzitsura.
- **Beharrezko bikoizketarik gabe**: bigarren mailako dokumentuek kanonikora estekatzen dute errepikatu beharrean.

## Indizea dokumentuka

| Documento | Qué cubre | Audiencia |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Utilidad real por rol y flujos (festival, inscripción, comités, premios, chat/E2EE) | usuario, admin, IA |
| [USO.md](USO.md) | Arranque, variables, migración SQLite↔MariaDB, backups, roles y operación | usuario, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoints `/api/admin`, cuenta inicial, rotación de secretos, límites, troubleshooting | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Perfiles Docker, puertos, volúmenes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, matriz `require_*`, perímetro, checklist producción | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Mapa sistema + reglas backend/frontend + flujos clave | dev, IA |
| [API.md](../es/API.md) | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.md](DESARROLLO.md) | Convención para añadir endpoint/pantalla + puertas CI | dev, IA |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Scripts `start.*`, builds distribuibles, Docker, fixes CI | dev |
| [PUSH.md](PUSH.md) | Decisión de notificaciones sin Firebase | dev |
| [DATABASE.md](DATABASE.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| [BACKEND.md](BACKEND.md) | Guía del backend (capas, config, auth, tests) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Informe de auditoría (rev. 10/10/2026) | referencia |

## Ibilbide gomendatua profilez

### Azken erabiltzailea

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) baimenak edo ingurune produktiboa berrikusi behar badituzte soilik

### Hedapen-administratzailea

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Garatzailea

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.md](../es/API.md)
5. [DATABASE.md](DATABASE.md)

## Dokumentazioa mantentzeko konbentzioak

- Eguneratu dokumentu kanonikoa edozein laburpen edo indize baino lehen.
- Abiarazte-fluxu bat aldatzen baduzu, sinkronizatu [README.md](../../README.eu.md), [USO.md](USO.md) eta [HERRAMIENTAS.md](HERRAMIENTAS.md).
- API publiko bat aldatzen baduzu, eguneratu [API.md](../es/API.md) eta, dagokionean, [DESARROLLO.md](DESARROLLO.md).
- Eskema edo iraunkortasuna aldatzen baduzu, berrikusi [DATABASE.md](DATABASE.md) eta migrazioak.

## FAQ azkarra

- **Nondik hasi?** Irakurri [USO.md](USO.md) app-a operatuko baduzu; irakurri [ARQUITECTURA.md](ARQUITECTURA.md) garatuko baduzu.
- **Zer da kanonikoa eta zer ez?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](../es/API.md) eta [DATABASE.md](DATABASE.md) dira gai horietarako erreferentzia ofiziala.
- **Non aurkitzen dut komando edo script bat?** Berrikusi [HERRAMIENTAS.md](HERRAMIENTAS.md) eta [../README.md](../../README.eu.md).
- **Nola jakin aldaketa batek dokumentazioa behar duen?** Abiarazte, baimen, azpiegitura, API edo datu-ereduan eragiten badu, dagokion dokumentazioan islatu behar da.

## Ikusi halaber

- [../README.md](../../README.eu.md): proiektuaren ikuspegi orokorra
- [USO.md](USO.md): operazioa eta tokiko konfigurazioa
- [ADMINISTRACION.md](ADMINISTRACION.md): hedapen- eta administrazio-esparrua
- [ARQUITECTURA.md](ARQUITECTURA.md): sistemaren mapa teknikoa
- [API.md](../es/API.md): endpoint-en erreferentzia

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

Proiektuaren komando eta profilen erreferentzia osoa [HERRAMIENTAS.md](HERRAMIENTAS.md)-n eta [../README.md](../../README.eu.md)-n dago.
