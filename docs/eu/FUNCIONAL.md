# Funtzionala — zer egin daitekeen Clakettes-en

[ES](../es/FUNCIONAL.md) · [EN](../en/FUNCIONAL.md) · [FR](../fr/FUNCIONAL.md) · [DE](../de/FUNCIONAL.md) · [IT](../it/FUNCIONAL.md) · [CA](../ca/FUNCIONAL.md) · [EU](FUNCIONAL.md) · [GL](../gl/FUNCIONAL.md) · [OC](../oc/FUNCIONAL.md)

Proiektuaren benetako erabilgarritasuna rol bakoitzeko, eusten dion fluxuarekin. Xehetasun operatiboa [USO.md](USO.md)-n, endpoint-en erreferentzia [API.md](../es/API.md)-n.

## Jaialdia (organizer)

1. Jaialdia sortzen du (`POST /api/festivals/`) deskribapen, web, egoitza eta logoarekin.
2. Deialdiak irekitzen ditu: izen-emate inprimakiak sekzio, rol eta etiketekin (`RegistrationForm + Sections + Links`), konturik gabe edonork bete dezakeen esteka publiko bidez azalduak.
3. Zure deialdiei lotutako laburrak eta errodaje-kokapenak jasotzen ditu.
4. Programazioa muntatzen du: ekitaldiak (gala, proiekzioa, tailerra, mahaia, networking-a, sariak, festa, masterclass-a, Q&A) sarrera-motak, eserlekuak (erabilgarri/erreserbatua/saldua/esleitua/blokeatua), erreserbak eta asistenten check-in-arekin; asistentak CSV-ra eta ekitaldiak ICS-ra esportatzen ditu.
5. Kide-dun batzordeak izendatzen ditu eta sariak argitaratzen ditu (egiaztatuak edo ez, publikoak edo ez) jaialdi, labur edo erabiltzaileko.
6. Komunikatzen du: jaialdiaren kanalak (admin/moderator/member), mezuak eta irudiak profilean, rulebook-ak.

Bere jaialdiak soilik editatzen/ezabatzen ditu eta bere erabiltzaileak kudeatzen ditu (`require_festival_admin`). Kideak bakarrik batzen dira `attendee` gisa; gainerako rolak admin batek esleitzen ditu (409 jada kide bada).

## Profesionala (user, jury, gainerako ofizioak)

- Ofizio-dun profila (zuzendaritza, interpretazioa, soinua, gidoia, muntaia, jantziak, makillajea, figurazioa, bikoizketa, foley, prentsa, ekoizpena, banaketa…), bio eta plataformako jaialdiei lotutako edo kanpo-estekazko palmaresa.
- Pribatutasuna eremuz eremu (email, bio, kokapena) eta profil publiko/pribatuak.
- Erabiltzaile bakoitzak bere profila eta bere laburrak editatzen ditu; epaimahaiak bere jaialdiaren arabera kontsultatu eta bozkatzen du.
- Txat zuzena eta talde/kanalekoa muturretik muturrerako zifraketarekin: giltza publikoak `POST /api/users/me/public-key`-n argitaratzen dira, zerbitzariak zifratua gorde eta birtransmititu soilik egiten du, benetako zifraketa app-ean gertatzen da.

## Ekipo express-a (attendee)

- Auto-join jaialdira (`POST /api/festivals/{id}/join`, `attendee` rolarekin) eta irteera askea (`leave`).
- Parte-hartzaileak geolokalizatzen ditu, taldea txatez koordinatzen du eta laburra express lehiaketara aurkezten du.
- Eserlekua erreserbatzen du ekitaldietan eta izen-emateak bidaltzen ditu esteka publiko bidez (egoerak: pendiente/aprobada/rechazada/en espera/cancelada; ordainketak: impagado/pendiente/pagado/reembolsado/cancelado).

## Publikoa

Jaialdiak deskubritzen ditu (`GET /api/festivals/` paginatua eta publikoa), laburrak eta palmaresa jarraitzen ditu, txatez kontaktatzen du eta egoitzak mapan kontsultatzen ditu.

## Admin globala (admin)

Dena ikusi eta editatzen du (erabiltzaileak, jaialdiak, laburrak, kanalak, inprimakiak). Operatiba [ADMINISTRACION.md](ADMINISTRACION.md)-n (stats, taulak, reset, backup-ak, sekretuak).

## Jakin behar dituzun egoerak

- Jaialdi-kidea: `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Izen-ematea: `draft → submitted → approved / rejected`; bidalketa: `pending / approved / rejected / waitlisted / cancelled`.
- Ekitaldi-asistentea: `registered / attended / no_show / cancelled`.
- Ekitaldien ikusgarritasun-helmena: `public / festival_members / roles / attendees_only`.
