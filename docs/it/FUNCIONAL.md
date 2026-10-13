# Funzionale — cosa si può fare in Clakettes

[ES](../es/FUNCIONAL.md) · [EN](../en/FUNCIONAL.md) · [FR](../fr/FUNCIONAL.md) · [DE](../de/FUNCIONAL.md) · [IT](FUNCIONAL.md) · [CA](../ca/FUNCIONAL.md) · [EU](../eu/FUNCIONAL.md) · [GL](../gl/FUNCIONAL.md) · [OC](../oc/FUNCIONAL.md)

Utilità reale del progetto per ruolo, con il flusso che la sostiene. Dettaglio operativo in [USO.md](USO.md), riferimento degli endpoint in [API.md](../es/API.md).

## Festival (organizer)

1. Crea il festival (`POST /api/festivals/`) con descrizione, web, sede e logo.
2. Apre bandi: form di iscrizione con sezioni, ruoli ed etichette (`RegistrationForm + Sections + Links`), esposti tramite link pubblico che chiunque può compilare senza account.
3. Riceve corti collegati ai tuoi bandi e location di ripresa.
4. Monta la programmazione: eventi (gala, proiezione, workshop, tavola, networking, premi, festa, masterclass, Q&A) con tipi di biglietto, posti (disponibile/prenotata/venduta/assegnata/bloccata), prenotazioni e check-in dei partecipanti; esporta partecipanti in CSV ed eventi in ICS.
5. Nomina comitati con membri e pubblica premi (verificati o no, pubblici o no) per festival, corto o utente.
6. Comunica: canali del festival (admin/moderator/member), messaggi e immagini nel profilo, rulebooks.

Edita/cancella solo i suoi festival e gestisce i suoi utenti (`require_festival_admin`). I membri si uniscono da soli come `attendee`; il resto dei ruoli lo assegna un admin (409 se è già membro).

## Professionista (user, jury, resto dei mestieri)

- Profilo con mestiere (regia, interpretazione, suono, sceneggiatura, montaggio, costumi, trucco, comparse, doppiaggio, foley, stampa, produzione, distribuzione…), bio e palmarès collegato a festival della piattaforma o esterno tramite link.
- Privacy campo per campo (email, bio, posizione) e profili pubblici/privati.
- Ogni utente modifica il suo profilo e i suoi corti; la giuria consulta e vota secondo il suo festival.
- Chat diretta e di gruppo/canale con cifratura end-to-end: le chiavi pubbliche si pubblicano in `POST /api/users/me/public-key`, il server salva e ritrasmette solo cifrato, la cifratura reale avviene nell'app.

## Squadra express (attendee)

- Auto-join al festival (`POST /api/festivals/{id}/join`, ruolo `attendee`) e uscita libera (`leave`).
- Geolocalizza partecipanti, coordina il gruppo via chat e presenta il corto al concorso express.
- Prenota il posto negli eventi e invia iscrizioni tramite link pubblico (stati: pendiente/aprobada/rechazada/en espera/cancelada; pagamenti: impagado/pendiente/pagado/reembolsado/cancelado).

## Pubblico

Scopre festival (`GET /api/festivals/` paginato e pubblico), segue corti e palmarès, contatta via chat e consulta le sedi sulla mappa.

## Amministratore globale (admin)

Vede e modifica tutto (utenti, festival, corti, canali, form). Operatività in [ADMINISTRACION.md](ADMINISTRACION.md) (stats, tabelle, reset, backup, segreti).

## Stati da conoscere

- Membro di festival: `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Iscrizione: `draft → submitted → approved / rejected`; invio: `pending / approved / rejected / waitlisted / cancelled`.
- Partecipante a evento: `registered / attended / no_show / cancelled`.
- Ambito di visibilità degli eventi: `public / festival_members / roles / attendees_only`.
