# Dokumentazioa — Clakettes

Hau da proiektu dokumentazioaren hasierako aukera. Erabiltzaile, administrativesa edo garatzaileari gida egokiena eskaintzen du, fitxategi auzaz lerro eskuratu gabe.

## Hizkuntzak

Dokumentazio osoa platformaren 9 hizketan dago. Eskainera (kanarioak) kanonikoa da:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

## Dokumentazioa navegatu

- **Aplikazioa erabiltzen nahi dut** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Deploiamentua administratorratzen dut** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Garatze** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md) + [BACKEND.md](BACKEND.md)
- **IA / agente** → [ARQUITECTURA.md](ARQUITECTURA.md) eta tasaren dokumentazioa; komando eta konbendio obligatzailea [../AGENTS.md](../../AGENTS.md) clickuan daude

## Dokumentazioen prinsipioak

- **Kanonikoko dokumentu bakarra gaiak bakoitzeko**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) eta [API.md](API.md) ofizialak dira aukerarenreferentzia.
- **Audienten arabera eskrita dokumentazioa**: gida bakoitza leker motaentzakoa da, komando batzuen kopuru batik gabe.
- **Erreferentzia lnkagunak**: non bai zerbitzunik aurretik badago.
- **Ez doan duplikazioa**: dokumentazio berriak kanonikoan ekarri egiten duena, ez bakarrik alkoholitzatzea.

## Dokumentazioen zerrenda

| Dokumentua | Zergatik dugu | Audientzia |
|------------|---------------|------------|
| [FUNCIONAL.md](FUNCIONAL.md) | Balio ekonomiko rolen arabera eta bidez (festival,registrement, komitetak, saria, xat/E2EE, juradoko bota) | erabiltzailea, admin, IA |
| [USO.md](USO.md) | Hasi, aldagaiak, SQLite↔MariaDB migrazioa, kopak, kideak, ondorio | erabiltzailea, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | `/api/admin` endpoints, hasiera kontua, secret rotaketa, ondorioak, problema burutzea | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Docker-profilak, portuak, bideuak, Nginx, norabidea, CI (GitHub + GitLab) | admin, garatzailea |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokenek, `require_*`-matrizua, bihurtzea, hogoa zizketa | admin, garatzailea |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Sistemaren mapa + backend/frontend gailuak + bidez handia | garatzailea, IA |
| [API.md](API.md) | Endpoint-eren inkesta (erakuskita `tools/gen_api.py`-ekin) | garatzailea, IA |
| [DESARROLLO.md](DESARROLLO.md) | Konbendio endpoint/pantalla gehitzeko + CI portuak | garatzailea, IA |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | `start.*` eskurak, konprezatutako gunoi, Docker, garatzeko fix | garatzailea |
| [PUSH.md](PUSH.md) | Notification-akerekutzeko aukerak Firebase ellenére | garatzailea |
| [DATABASE.md](DATABASE.md) | Dual SQLite/MariaDB esku, modelo-aren fichak, ER | garatzailea, IA |
| [BACKEND.md](BACKEND.md) | Backend-gidea (nazio, konfigurazioa, autentikazioa, proveek) | garatzailea |
| [AUDITORIA.md](AUDITORIA.md) | Auditen aurkezpena (10/10/2026, rev) | ahulpen |
| [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md) | Noden arteko federazio protokoloa (fase 4) | garatzailea, IA |
| [FEDERATION_SCHEMA.md](FEDERATION_SCHEMA.md) | Clakettes Schema v1 (minimale federatutako eskuroak) | garatzailea, IA |
| [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) | Federatutako confianzaaren modeloa, mTLS, sertifikatu rotazioa | garatzailea, IA |

## Bidaia garatzailearen arabera

### Erabiltzailea

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) zizketarenהקדمة bezala

### Deploiamentu admin

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

## Dokumentazioa konbendioak

- Aldatu dokumentazioa lehenago eta ondoren aldaketa mapa.
- Aldaketa hazkundeari ekarri nahi baduzu, sinkronizatze [README.eu.md](../../README.eu.md), [USO.md](USO.md) eta [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Aldaketa API-ak public alderantziz nahi baduzu, alderantziz [API.md](API.md) eta, eskaintzan, [DESARROLLO.md](DESARROLLO.md).
- Aldaketa eskupena aldatu nahi baduzu, keri [DATABASE.md](DATABASE.md) eta migrazioak.
- Aldaketa egin baduzu `docs/es/` fitxategi batean, errepikatu aldi 8 gaztelako (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## Auzoan aurkeztuak

- **Hasi nora?** Erakuskite [USO.md](USO.md) aplikazioa aukeratzeko; [ARQUITECTURA.md](ARQUITECTURA.md) garatzeko.
- **Zer da kanonikoa eta zer ez?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) eta [DATABASE.md](DATABASE.md) ofizialak dira aukerakarenreferentziak.
- **Norkor komandoa edo eskuatea aurkitu nahi baduzu?** [HERRAMIENTAS.md](HERRAMIENTAS.md) eta [../README.eu.md](../../README.eu.md).
- **Nola jakite nahi badut dokumentazioa behar?** Aldaketa hasi, kideketak, erlan, API edo modeloa aldatu nahi baduzu, dokumentazio egokietan aldatu beharko duzu.

## Aurora berezia

- [../README.eu.md](../../README.eu.md): proiektoren oharra
- [USO.md](USO.md): oinarrizko erlan etiketatzeko
- [ADMINISTRACION.md](ADMINISTRACION.md): deploiamentuaren eta administrazioa
- [ARQUITECTURA.md](ARQUITECTURA.md): sistemaren mapa teknikoa
- [API.md](API.md): endpoint-eren oharra

## Ezaugarritako hasiera

Hasieran entornu batean:

```bash
cd backend && python -m uvicorn app.main:app --reload
cd frontend && flutter run
```

Bakoitzaren erabiltzen:

```bat
start.bat --dev
```

Komando eta perfilen oharra [HERRAMIENTAS.md](HERRAMIENTAS.md) eta [../README.eu.md](../../README.eu.md).