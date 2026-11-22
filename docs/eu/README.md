# Dokumentazioa — Clakettes

Aurkibide hau proiektuaren dokumentazioaren sarrera nagusia da. Erabiltzaile, administratzaile edo garatzaile batek gida egokia aurki dezan pentsatuta dago, ausaz fitxategiak irakurri gabe.

## Hizkuntzak

18 dokumentu komunak plataformaren 9 hizkuntzetan daude; `docs/es/`-n bi azterketa espezifiko ere badaude (`AMENAZAS_NODOS_FEDERACION.md` eta `MODELO_CONFIANZA_NODOS.md`). Espainiera (kanarioa) da kanonikoa:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

## Dokumentazioan nabigatzen

- **Aplikazioa erabili nahi dut** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Inplementazio bat administratzen dut** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Garapena** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md) + [BACKEND.md](BACKEND.md) + [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md)
- **Agenteentzako erreferentzia** → garapeneko komandoak eta konbentzioak [../AGENTS.md](../../AGENTS.md) fitxategian daude

## Dokumentazioaren printzipioak

- **Gai bakoitzeko dokumentu kanoniko bakarra**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) eta [API.md](API.md) dira beren arloko erreferentzia ofiziala.
- **Publikoaren araberako dokumentazioa**: gida bakoitza irakurle mota bati zuzenduta dago, komando multzo bakar bati baino gehiago.
- **Lotura zuzenak**: hemendik eduki garrantzitsura klik bakarrean irits daiteke.
- **Beharrezkoa ez den bikoizketarik ez**: bigarren mailako dokumentuek kanonikora lotzen dute, errepikatu beharrean.

## Dokumentuen aurkibidea

| Dokumentua | Zer estaltzen du | Publikoa |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Benetako erabilgarritasuna rolaren arabera eta fluxuak (jaialdia, izena-ematea, batzordeak, sariak, txata/E2EE, epaimahaiaren botoa) | erabiltzailea, admin |
| [USO.md](USO.md) | Abiaraztea, aldagaiak, SQLite↔MariaDB migrazioa, babeskopiak, rolak eta operazioa | erabiltzailea, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | `/api/admin` endpoint-ak, hasierako kontua, sekretuen birzirkulazioa, mugak, arazoak konpontzea | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Docker profilak, atak, bolumenak, Nginx, osasuna, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokenak, `require_*` matrizea, perimetroa, ekoizpenerako kontrol-zerrenda | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Sistemaren mapa + backend/frontend arauak + fluxu giltzarriak | dev |
| [API.md](API.md) | Endpoint-en erreferentzia | dev |
| [DESARROLLO.md](DESARROLLO.md) | Endpoint/pantaila berria gehitzeko konbentzioa + CI ateak | dev |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | `start.*` script-ak, banaketarako build-ak, Docker, CI konponketak | dev |
| [PUSH.md](PUSH.md) | Firebase gabe jakinarazpenen erabakia | dev |
| [DATABASE.md](DATABASE.md) | SQLite/MariaDB eskema duala, modelo bakoitzeko fitxak, ER | dev |
| [BACKEND.md](BACKEND.md) | Backendaren gida (geruzak, konfigurazioa, autentifikazioa, testak) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Auditoretza txostena (berrik. 10/10/2026) | erreferentzia |
| [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md) | Nodoen arteko federazio-protokoloa (2tik 10erako faseak) | dev |
| [FEDERATION_SCHEMA.md](FEDERATION_SCHEMA.md) | Clakettes Schema v1 (gutxieneko entitate federatuak) | dev |
| [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) | Federazio-confiantza eredua, mTLS, sinatutako manifestua, portabilitatea, txata eta erresilientzia | dev |
| [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md) | Nodoen arteko txat eta gertaeretarako broker-erabakia (NATS JetStream); gaur egun inplementatutako garraioa: `DurableQueueBackend` `chat_outbox`-en WebSocket ertzekoarekin | dev |
| [AMENAZAS_NODOS_FEDERACION.md](../es/AMENAZAS_NODOS_FEDERACION.md) | Federazio-nodoen mehatxu-eredua (soilik gaztelaniaz) | dev |
| [MODELO_CONFIANZA_NODOS.md](../es/MODELO_CONFIANZA_NODOS.md) | Nodoen arteko konfiantza-eredua (soilik gaztelaniaz) | dev |

## Profilaren araberako ibilbide gomendatua

### Azken erabiltzailea

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) soilik baimenak edo ekoizpen-ingurunea berrikusi behar baditu

### Inplementazioaren administratzailea

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Garatzailea

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.md](API.md)
5. [DATABASE.md](DATABASE.md)
6. [BACKEND.md](BACKEND.md)
7. [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md)
8. [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md)
9. [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md)

## Dokumentazioa mantentzeko konbentzioak

- Eguneratu dokumentu kanonikoa laburpen edo aurkibide edozein baino lehen.
- Abiarazte-fluxuren bat aldatzen baduzu, sinkronizatu [README.eu.md](../../README.eu.md), [USO.md](USO.md) eta [HERRAMIENTAS.md](HERRAMIENTAS.md).
- API publikoren bat aldatzen baduzu, eguneratu [API.md](API.md) eta, hala badagokio, [DESARROLLO.md](DESARROLLO.md).
- Eskema edo iraunkortasuna aldatzen baduzu, berrikusi [DATABASE.md](DATABASE.md) eta migrazioak.
- `docs/es/` fitxategi bat editatzen duzun bakoitzean, errepikatu aldaketa 8 ahizpetan (`docs/<hizkuntza>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## Ohiko galderak

- **Non hasi?** Irakurri [USO.md](USO.md) aplikazioa operatzeko, edo [ARQUITECTURA.md](ARQUITECTURA.md) garatzeko.
- **Zer da kanonikoa eta zer ez?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) eta [DATABASE.md](DATABASE.md) dira gai horien erreferentzia ofiziala.
- **Non aurkitu komando edo script bat?** Berrikusi [HERRAMIENTAS.md](HERRAMIENTAS.md) eta [../README.eu.md](../../README.eu.md).
- **Nola jakin aldaketa batek dokumentazioa behar duen?** Abiaraztea, baimenak, azpiegitura, APIa edo datu-eredua ukitzen badu, dagokion dokumentazioan jaso behar da.

## Ikus ere

- [../README.eu.md](../../README.eu.md): proiektuaren ikuspegi orokorra
- [USO.md](USO.md): tokiko operazioa eta konfigurazioa
- [ADMINISTRACION.md](ADMINISTRACION.md): inplementazioaren eta administrazioaren esparrua
- [ARQUITECTURA.md](ARQUITECTURA.md): sistemaren mapa teknikoa
- [API.md](API.md): endpoint-en erreferentzia
