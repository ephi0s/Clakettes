# Funzionale — cosa si può fare in Clakettes

[ES](../es/FUNCIONAL.md) · [EN](../en/FUNCIONAL.md) · [FR](../fr/FUNCIONAL.md) · [DE](../de/FUNCIONAL.md) · [IT](FUNCIONAL.md) · [CA](../ca/FUNCIONAL.md) · [EU](../eu/FUNCIONAL.md) · [GL](../gl/FUNCIONAL.md) · [OC](../oc/FUNCIONAL.md)

Utilità reale del progetto per ruolo, con il flusso che la sostiene. Dettaglio operativo in [USO.md](USO.md), riferimento degli endpoint in [API.md](API.md).

## Festival (organizzatore)

1. Crea il festival (`POST /api/festivals/`) con descrizione, sito web, sede e logo.
2. Apre le call: moduli di iscrizione con sezioni, ruoli ed etichette (`RegistrationForm + Sections + Links`), esposti tramite link pubblico che chiunque può compilare senza account.
3. Riceve i corti legati alle tue call e le location di ripresa, gestiti in `/api/festivals/{id}/shortfilms` e classificati come `official_section` (predefinito) o `contest`; il profilo del festival mostra il conteggio e l'app permette di filtrare per tipo.
4. Allestisce la programmazione: eventi (gala, proiezione, workshop, tavola, networking, premi, festa, masterclass, Q&A) con tipi di biglietto, posti (disponibile/prenotato/venduto/assegnato/bloccato), prenotazioni e check-in dei partecipanti; esporta i partecipanti in CSV e gli eventi in ICS. Scevera ogni opera della visionatura con stato `pending/screened/disqualified` e motivo, e filtra per stato, squalificati o etichetta del partecipante. Si possono programmare solo proiezioni con corti dello stesso festival (`EventService` rifiuta gli id estranei). L'organizzazione verifica le etichette di eleggibilità dei partecipanti (residente, studente) con metodi esterni, e il partecipante può richiedere la verifica allegando un certificato di residenza o di iscrizione.
5. Nomina comitati con membri e pubblica premi (verificati o no, pubblici o no) per festival, corto o utente, con etichette di eleggibilità e verifica del destinatario.
6. Comunica: canali del festival (admin/moderator/member), messaggi e immagini sul profilo, rulebook.

Modifica/cancella solo i propri festival e gestisce i propri utenti (`require_festival_admin`). I membri si uniscono da soli come `attendee`; gli altri ruoli sono assegnati da un admin (409 se già membro).

## Professionista (utente, giuria, altri mestieri)

- Profilo con mestiere (regia, recitazione, suono, sceneggiatura, montaggio, costume, trucco, comparso, doppiaggio, foley, stampa, produzione, distribuzione…), bio e palmarès legati ai festival della piattaforma o esterni tramite link.
- Privacy campo per campo (email, bio, posizione) e profili pubblici/privati.
- Ogni utente modifica il proprio profilo e i propri corti; la giuria consulta e vota in base al proprio festival e può votare solo i corti di esso.
- Chat diretta e di gruppo/canale con cifratura end-to-end: le chiavi pubbliche sono pubblicate su `POST /api/users/me/public-key`, il server memorizza e inoltra solo dati cifrati, la vera cifratura avviene nell'app. Tra nodi federati il messaggio passa dal bridge firmato, viene deduplicato per `message_id` e ordinato per data; puoi segnalare messaggi e gli amministratori possono silenziare utenti o filtrare parole. L'app mostra indicatore di scrittura, latenza e conferme di lettura, consente la ricerca nella cronologia e accoda i messaggi offline in modo duraturo con lo stesso `message_id`.

## Squadra express (attendee)
- Il concorso express (chiamato anche guerrilla) è il concorso cittadino **dentro il festival**: i corti si creano e si votano con `contest_type = contest` (il valore predefinito è `official_section`; express e guerrilla sono lo stesso concorso).

- Auto-join al festival (`POST /api/festivals/{id}/join`, ruolo `attendee`) e uscita libera (`leave`).
- Geolocalizza i partecipanti, coordina il gruppo tramite chat e presenta il corto al concorso express.
- Prenota un posto agli eventi e invia iscrizioni tramite link pubblico (stati: in attesa/approvato/rifiutato/in lista d'attesa/annullato; pagamenti: non pagato/in attesa/pagato/rimborsato/annullato).

## Pubblico

Scopre i festival (`GET /api/festivals/` paginato e pubblico), segue corti e palmarès, contatta tramite chat e consulta le sedi sulla mappa.

## Amministratore globale (admin)

Vede e modifica tutto (utenti, festival, corti, canali, moduli). Gestione in [ADMINISTRACION.md](ADMINISTRACION.md) (statistiche, tabelle, reset, backup, segreti). Nella federazione registra i nodi e le loro politiche (`import_only`, `disable_chat`, `disable_search`), esporta e importa bundle, migra festival e identità utente con i loro redirect, pubblica eventi, modera la chat e vigila sulla resilienza (metriche p50/p95 e revoca delle chiavi).

## Giuria (juror)

- Consulta le opere assegnate al proprio festival ed esprime voti per corto (`POST /api/jury-votes/`).
- Punteggio per opera con aggregazione automatica; anonimato opzionale.
- Consulta i risultati aggregati per gli organizzatori.

## Stati da conoscere

- Membro del festival: `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Iscrizione: `draft → submitted → approved / rejected`; invio: `pending / approved / rejected / waitlisted / cancelled`.
- Partecipante a evento: `registered / attended / no_show / cancelled`.
- Sceveratura in proiezione: `pending / screened / disqualified`.
- Note della giuria e verbali per opera, con annotazione: `special_mention / accesit / other`.
- Verifica etichetta partecipante: `unverified / pending / verified / rejected`.
- Ambito di visibilità degli eventi: `public / festival_members / roles / attendees_only`.

## Vedi anche

- [USO.md](USO.md): avvio e gestione del sistema
- [API.md](API.md): riferimento degli endpoint
- [ADMINISTRACION.md](ADMINISTRACION.md): amministrazione del deployment
