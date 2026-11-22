# Funcional — qu'es possible de far amb Clakettes

[ES](../es/FUNCIONAL.md) · [EN](../en/FUNCIONAL.md) · [FR](../fr/FUNCIONAL.md) · [DE](../de/FUNCIONAL.md) · [IT](../it/FUNCIONAL.md) · [CA](../ca/FUNCIONAL.md) · [EU](../eu/FUNCIONAL.md) · [GL](../gl/FUNCIONAL.md) · [OC](FUNCIONAL.md)

Utilitat reala del projècte per ròtle, amb lo flux que la sosten. Detalh operatiu dins [USO.md](USO.md), referéncia dels endpoints dins [API.md](API.md).

## Festival (organizer)

1. Crea lo festival (`POST /api/festivals/`) amb descripcion, web, sèti e logo.
2. Dobra las convocacions: formularis d'inscripcion amb seccions, ròtles e etiquetas (`RegistrationForm + Sections + Links`), expausats per un ligam public que qualqu'un pòt emplir sens compte.
3. Receb los corts ligats a las tuas convocacions e localizacions de rodatge.
4. Monta la programacion: eveniments (gala, projeccion, atelier, taula, networking, prèmis, fèsta, masterclass, Q&A) amb tipes de bilhet, sètis (disponible/reservada/vendida/asignada/bloquejada), reservas e check-in dels assistents; exporta los assistents a CSV e los eveniments a ICS. Criba cada òbra del visionatge amb estat `pending/screened/disqualified` e motiv, e filtra per estat, desqualificadas o etiqueta de participant. L'organizacion verifica las etiquetas d'elegibilitat (resident, estudiant) amb de metòdes externs, e lo participant pòt demandar la verificacion en apondent un certificat de residéncia o d'inscripcion.
5. Nomena de comitats amb de membres e publica de prèmis (verificats o non, publics o non) per festival, cort o usagi, amb etiquetas d'elegibilitat e verificacion del receptor.
6. Comunica: los canales del festival (admin/moderator/member), messatges e imatges sul perfil, rulebooks.

Solament edita/escafa sos festivals e gestiona sos usagis (`require_festival_admin`). Los membres s'adjonhon sols coma `attendee`; los autres ròtles los atribuís un admin (409 se ja es membre).

## Professional (user, jury, autres mestièrs)

- Perfil amb mestièr (realizacion, interpretacion, son, scenario, montatge, vestuari, maquilhaje, figuracion, doblatge, foley, premsa, produccion, distribucion…), bio e palmarés ligat als festivals de la plataforma o extern per ligam.
- Privacitat camp per camp (email, bio, localizacion) e perfils publics/privats.
- Cada usagi edita son perfil e sos corts; lo jurat consulta e vota segon son festival.
- Chat dirècte e de grop/canal amb chiframent de cap a cap: las claus publicas son publicadas a `POST /api/users/me/public-key`, lo servidor serva e retransmet solament lo chifrat, lo chiframent real se passa dins l'app. Ente noses federats lo messatge viatja pel bridge signat, es deduplicat per `message_id` e ordenat per data; podetz senhalar de messatges e los administrators pòdon silenciar d'usagis o filtrar de mots.

## Equipa express (attendee)
- Lo concors express (tanben dich guerrilla) es lo concors ciutadan **dins lo festival** : los corts son creats e votats amb `contest_type = contest`.

- Auto-join al festival (`POST /api/festivals/{id}/join`, ròtle `attendee`) e sortida liura (`leave`).
- Ge-localiza los participants, coordona lo grop per chat e presenta lo cort al concors express.
- Reserva un sèti dins los eveniments e envia d'inscripcions per ligam public (estats: pendent/aprovada/regetada/en espèra/cancelada; pagaments: impagat/pendent/pagat/reemborsat/cancelat).

## Public

Descobrís los festivals (`GET /api/festivals/` paginat e public), seguís los corts e lo palmarés, contacta per chat e consulta los sètis sus la mapa.

## Administrator general (admin)

Vej e edita tot (usagis, festivals, corts, canales, formularis). Operativa dins [ADMINISTRACION.md](ADMINISTRACION.md) (stats, taulas, reset, còpias de seguretat, secrets). En federacion enregistra los noses e lor politicas (`import_only`, `disable_chat`, `disable_search`), exporta e importa de bundles, migra los festivals e las identitats d'usagis amb lor redireccions, publica d'eveniments, modera lo chat e vigila la resiliéncia (metricas p50/p95 e revocacion de claus).

## Jurat (juror)

- Consulta las òbras atribuidas a son festival e emet de vòtes per cort (`POST /api/jury-votes/`).
- Notacion per òbra amb agregacion automatica; anonimat opcional.
- Consulta los resultats agregats pels organizers.

## Estats que cal conéisser

- Membre de festival: `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Inscripcion: `draft → submitted → approved / rejected`; enviament: `pending / approved / rejected / waitlisted / cancelled`.
- Assistent a eveniment: `registered / attended / no_show / cancelled`.
- Cribatge en projeccion: `pending / screened / disqualified`.
- Notas del jurat e actas per òbra, amb anotacion: `special_mention / accesit / other`.
- Verificacion d'etiqueta de participant: `unverified / pending / verified / rejected`.
- Domeni de visibilitat dels eveniments: `public / festival_members / roles / attendees_only`.

## Vejatz tanben

- [USO.md](USO.md): arranjada e operacion del sistèma
- [API.md](API.md): referéncia dels endpoints
- [ADMINISTRACION.md](ADMINISTRACION.md): administracion del desplegament
