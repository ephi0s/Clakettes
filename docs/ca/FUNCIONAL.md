# Funcional — què es pot fer a Clakettes

[ES](../es/FUNCIONAL.md) · [EN](../en/FUNCIONAL.md) · [FR](../fr/FUNCIONAL.md) · [DE](../de/FUNCIONAL.md) · [IT](../it/FUNCIONAL.md) · [CA](FUNCIONAL.md) · [EU](../eu/FUNCIONAL.md) · [GL](../gl/FUNCIONAL.md) · [OC](../oc/FUNCIONAL.md)

Utilitat real del projecte per rol, amb el flux que la sosté. Detall operatiu a [USO.md](USO.md), referència d'endpoints a [API.md](API.md).

## Festival (organizer)

1. Crea el festival (`POST /api/festivals/`) amb descripció, web, seu i logo.
2. Obre convocatòries: formularis d'inscripció amb seccions, rols i etiquetes (`RegistrationForm + Sections + Links`), exposats per enllaç públic que qualsevol pot omplir sense compte.
3. Rep curts vinculats a les teves convocatòries i localitzacions de rodatge.
4. Munta la programació: esdeveniments (gala, projecció, taller, taula, networking, premis, festa, masterclass, Q&A) amb tipus d'entrada, seients (disponible/reservada/venuda/assignada/bloquejada), reserves i check-in d'assistents; exporta assistents a CSV i esdeveniments a ICS. Criba cada obra del visionat amb estat `pending/screened/disqualified` i motiu, i filtra per estat, desqualificades o etiqueta de participant. L'organització verifica les etiquetes d'elegibilitat (resident, estudiant) amb mètodes externs, i el participant pot sol·licitar la verificació adjuntant certificat de residència o matrícula.
5. Nomena comitès amb membres i publica premis (verificats o no, públics o no) per festival, curt o usuari, amb etiquetes d'elegibilitat i verificació del receptor.
6. Comunica: canals del festival (admin/moderator/member), missatges i imatges al perfil, rulebooks.

Només edita/borra els seus festivals i gestiona els seus usuaris (`require_festival_admin`). Els membres s'uneixen sols com a `attendee`; la resta de rols els assigna un admin (409 si ja és membre).

## Professional (user, jury, resta d'oficis)

- Perfil amb ofici (direcció, interpretació, so, guió, muntatge, vestuari, maquillatge, figuració, doblatge, foley, premsa, producció, distribució…), bio i palmarès vinculat a festivals de la plataforma o extern per enllaç.
- Privacitat camp per camp (email, bio, ubicació) i perfils públics/privats.
- Cada usuari edita el seu perfil i els seus curts; el jurat consulta i vota segons el seu festival.
- Xat directe i de grup/canal amb xifrat d'extrem a extrem: les claus públiques es publiquen a `POST /api/users/me/public-key`, el servidor només desa i retransmet xifrat, el xifrat real occorre a l'app. Entre nodes federats el missatge viatja pel bridge signat, es deduplica per `message_id` i s'ordena per data; pots reportar missatges i els administradors poden silenciar usuaris o filtrar paraules.

## Equip express (attendee)

- Auto-join al festival (`POST /api/festivals/{id}/join`, rol `attendee`) i sortida lliure (`leave`).
- Geolocalitza participants, coordina el grup per xat i presenta el curt al concurs express.
- Reserva seient en esdeveniments i envia inscripcions per enllaç públic (estats: pendent/aprovada/rebutjada/en espera/cancel·lada; pagaments: impagat/pendent/pagat/reembossat/cancel·lat).

## Públic

Descobreix festivals (`GET /api/festivals/` paginat i públic), segueix curts i palmarès, contacta per xat i consulta seus al mapa.

## Administrador global (admin)

Ho veu i ho edita tot (usuaris, festivals, curts, canals, formularis). Operativa a [ADMINISTRACION.md](ADMINISTRACION.md) (stats, taules, reset, backups, secrets). En federació registra nodes i les seves polítiques (`import_only`, `disable_chat`, `disable_search`), exporta i importa bundles, migra festivals i identitats d'usuari amb les seves redireccions, publica esdeveniments, modera el xat i vigila la resiliència (mètriques p50/p95 i revocació de claus).

## Jurat (juror)

- Consulta les obres assignades al seu festival i emet vots per curt (`POST /api/jury-votes/`).
- Puntuació per obra amb agregació automàtica; anonimat opcional.
- Consulta resultats agregats per a organitzadors.

## Estats que has de conèixer

- Membre de festival: `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Inscripció: `draft → submitted → approved / rejected`; enviament: `pending / approved / rejected / waitlisted / cancelled`.
- Assistent a esdeveniment: `registered / attended / no_show / cancelled`.
- Cribratge en projecció: `pending / screened / disqualified`.
- Notes del jurat i actes per obra, amb anotació: `special_mention / accesit / other`.
- Verificació d'etiqueta de participant: `unverified / pending / verified / rejected`.
- Abast de visibilitat d'esdeveniments: `public / festival_members / roles / attendees_only`.

## Vegeu també

- [USO.md](USO.md): arrancada i operació del sistema
- [API.md](API.md): referència d'endpoints
- [ADMINISTRACION.md](ADMINISTRACION.md): administració del desplegament
