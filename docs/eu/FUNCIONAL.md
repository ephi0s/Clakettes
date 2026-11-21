# Funtzionala — Clakettes-ekin zer egin daitekeen

[ES](../es/FUNCIONAL.md) · [EN](../en/FUNCIONAL.md) · [FR](../fr/FUNCIONAL.md) · [DE](../de/FUNCIONAL.md) · [IT](../it/FUNCIONAL.md) · [CA](../ca/FUNCIONAL.md) · [EU](FUNCIONAL.md) · [GL](../gl/FUNCIONAL.md) · [OC](../oc/FUNCIONAL.md)

Proiektuaren benetako erabilgarritasuna rolaren arabera, harentzako fluxuarekin. Operazio-xehetasuna [USO.md](USO.md) fitxategian, endpoint-en erreferentzia [API.md](API.md) fitxategian.

## Jaialdia (organizer)

1. Sortu jaialdia (`POST /api/festivals/`) deskribapena, webgunea, egoitza eta logoarekin.
2. Ireki deialdiak: izena-emateko formularioak atal, rol eta etiketekin (`RegistrationForm + Sections + Links`), edonork konturik gabe bete dezakeen esteka publiko bidez erakutsita.
3. Jaso zure deialdiei eta errodatze-kokapenei lotutako film laburrak.
4. Antolatu programazioa: gertaerak (gala, proiekzioa, tailerra, mahingaia, networking-a, sariak, festa, masterclass-a, Q&A) sarrera-motak, eserlekuak (disponible/reservada/vendida/asignada/bloqueada), erreserbak eta bertaratuen check-in-arekin; esportatu bertatuak CSV-ra eta gertaerak ICS-ra. Proiekzioko lan bakoitza `pending/screened/disqualified` egoerarekin eta arrazoiarekin bahetu, eta egoera, deskalifikatuak edo parte-hartzailearen etiketaren arabera iragazi. Erakundeak elegibilitate-etiketak (bizilaguna, ikaslea) kanpoko metodoen bidez egiaztatzen ditu, eta parte-hartzaileak egiaztapena eska dezake bizileku edo matrikula ziurtagiria erantsiz.
5. Izendatu batzordeak kideekin eta argitaratu sariak (egiaztatuta edo ez, publikoak edo ez) jaialdi, film labur edo erabiltzaile bakoitzeko, elegibilitate-etiketekin eta hartzailearen egiaztapenarekin.
6. Komunikatu: jaialdiaren kanalak (admin/moderator/member), mezuak eta irudiak profilaren rulebook-ak.

Bere jaialdiak soilik editatu/ezabatu eta bere erabiltzaileak kudeatzen ditu (`require_festival_admin`). Kideak beren kabuz batzen dira `attendee` gisa; gainerako rolak admin batek esleitzen ditu (409 dagoeneko kidea bada).

## Profesionala (user, jury, gainerako ofizioak)

- Ofizioarekin profila (zuzendaritza, interpretazioa, soinua, gidoia, muntaketa, jantziak, makillajea, figurazioa, bikoizketa, foley, prentsa, ekoizpena, banaketa…), bioa eta plataformako jaialdiekin edo kanpoko estekarekin lotutako palmaresa.
- Eremuz eremuko pribatutasuna (email, bio, kokapena) eta profil publikoak/pribatuak.
- Erabiltzaile bakoitzak bere profila eta film laburrak editatzen ditu; epaimahaiak bere jaialdiaren arabera kontsultatu eta bozkatzen du.
- Zuzeneko eta talde/kanaleko txata muturretik muturrerako zifratuekin: gako publikoak `POST /api/users/me/public-key` bidez argitaratzen dira, zerbitzariak zifratuta soilik gorde eta birbidaltzen du, benetako zifratzea aplikazioan gertatzen da. Federatutako nodoen artean mezua sinatutako bridge-aren bidez bidaiatzen da, `message_id` bidez deduplikatzen da eta dataren arabera ordenatzen da; mezuak salatu ditzakezu eta administratzaileek erabiltzaileak isilarazi edo hitzak iragazi ditzakete.

## Express taldea (attendee)

- Auto-join jaialdian (`POST /api/festivals/{id}/join`, `attendee` rola) eta nahi gabe irtetea (`leave`).
- Parte-hartzaileak geolokalizatu, taldea txat bidez koordinatu eta film laburra express lehiaketara aurkeztu.
- Gertaeretan eserlekua erreserbatu eta izena-emateak esteka publiko bidez bidali (egoerak: pending/approved/rejected/en espera/cancelled; ordainketak: impagado/pendiente/pagado/reembolsado/cancelado).

## Publikoa

Ezagutu jaialdiak (`GET /api/festivals/` orrikatuta eta publikoa), jarraitu film laburrak eta palmaresa, txatez jarri harremanetan eta egoitzak mapan kontsultatu.

## Administratzaile globala (admin)

Guztia ikusi eta editatzen du (erabiltzaileak, jaialdiak, film laburrak, kanalak, formularioak). Operazioa [ADMINISTRACION.md](ADMINISTRACION.md) fitxategian (stats, taulak, reset, babeskopiak, sekretuak). Federazioan nodoak eta haien politikak erregistratzen ditu (`import_only`, `disable_chat`, `disable_search`), bundle-ak esportatu eta inportatzen ditu, jaialdiak eta erabiltzaile-identitateak haien birbideratzeekin migratzen ditu, gertaerak argitaratzen ditu, txata moderatzen du eta erresilientzia zaintzen du (p50/p95 metrikak eta gakoen errebokazioa).

## Epaimahaia (juror)

- Bere jaialdian esleitutako lanak kontsultatu eta film laburreko botoak eman (`POST /api/jury-votes/`).
- Lan bakoitzeko puntuazioa agregazio automatikoarekin; anonimotasun aukerakoa.
- Antolatzaileentzako emaitza agregatuak kontsultatu.

## Ezagutu beharreko egoerak

- Jaialdiko kidea: `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Izena-ematea: `draft → submitted → approved / rejected`; bidalketa: `pending / approved / rejected / waitlisted / cancelled`.
- Ekitaldiko bertaratua: `registered / attended / no_show / cancelled`.
- Proiekzio-baheketa: `pending / screened / disqualified`.
- Epaimahaiaren oharrak eta lan bakoitzeko aktak, oharpenarekin: `special_mention / accesit / other`.
- Parte-hartzailearen etiketaren egiaztapena: `unverified / pending / verified / rejected`.
- Gertaeren ikusgarritasun-eremua: `public / festival_members / roles / attendees_only`.

## Ikus ere

- [USO.md](USO.md): sistemaren abiaraztea eta operazioa
- [API.md](API.md): endpoint-en erreferentzia
- [ADMINISTRACION.md](ADMINISTRACION.md): inplementazioaren administrazioa
