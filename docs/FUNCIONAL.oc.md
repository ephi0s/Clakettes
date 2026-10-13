# Fonctionau — çò que se pòt far en Clakettes

Utilitat reala del projècte per ròtle, amb lo flux que la sosten. Detalh operatiu en [USO.oc.md](USO.oc.md), referéncia d'endpoints en [API.oc.md](API.oc.md).

## Festivau (organizer)

1. Crea lo festivau (`POST /api/festivals/`) amb descripcion, web, sèti e lògo.
2. Dubrís convocatòrias: formularis d'inscripcion amb seccions, ròtles e etiquetes (`RegistrationForm + Sections + Links`), expausats per ligam public que qual que siá pòt emplenar sens compte.
3. Recep corts ligats a tas convocatòrias e localizacions de rodatge.
4. Mònta la programacion: eveniments (gala, projeccion, talhièr, taula, networking, prèmis, fèsta, masterclass, Q&A) amb tipes de bilhet, sèts (disponible/reservada/venduda/assignada/blocada), resèrvas e check-in d'assistents; expòrta assistents cap a CSV e eveniments cap a ICS.
5. Nòmma comitats amb membres e publica prèmis (verificats o non, publics o non) per festivau, cort o utilizaire.
6. Comunica: canaus del festivau (admin/moderator/member), messatges e imatges dins lo perfil, rulebooks.

Sonque edita/escafa sos festivals e gerís sos utilizaires (`require_festival_admin`). Los membres se jóntan sols coma `attendee`; la rèsta de ròtles los assigna un admin (409 se ja es membre).

## Professionau (user, jury, rèsta de mestièrs)

- Perfil amb ofici (direccion, interpretacion, son, guion, montatge, vestuari, maquilhament, figuracion, doblatge, foley, premsa, produccion, distribucion…), bio e palmarés ligat a festivals de la plataforma o externe per ligam.
- Privacitat camp per camp (email, bio, ubicacion) e perfils publics/privats.
- Cada utilizaire edita son perfil e sos corts; lo jurat consulta e vòta segon son festivau.
- Chat dirècte e de grop/canau amb chiframent d'extrèm a extrèm: las claus publicas se publican en `POST /api/users/me/public-key`, lo servidor sonque garda e retransmet chifrat, lo chiframent vertadièr a luòc dins l'app.

## Equipa exprèss (attendee)

- Auto-join al festivau (`POST /api/festivals/{id}/join`, ròtle `attendee`) e sortida liura (`leave`).
- Geolocaliza participants, coordina lo grop per chat e presenta lo cort al concors exprèss.
- Resèrva sèti en eveniments e manda inscripcions per ligam public (estats: pendenta/aprobada/refusada/en espèra/anulada; pagaments: impagat/pendent/pagat/reemborsat/anulat).

## Public

Descobrís festivals (`GET /api/festivals/` paginat e public), seguís corts e palmarés, contacta per chat e consulta sèts sus la mapa.

## Administrator globau (admin)

O vei e o edita tot (utilizaires, festivals, corts, canaus, formularis). Operativa en [ADMINISTRACION.oc.md](ADMINISTRACION.oc.md) (stats, taulas, reset, salvagardas, secrets).

## Estats que devetz conéisser

- Membre de festivau: `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Inscripcion: `draft → submitted → approved / rejected`; mandadís: `pending / approved / rejected / waitlisted / cancelled`.
- Assistent a eveniment: `registered / attended / no_show / cancelled`.
- Portada de visibilitat d'eveniments: `public / festival_members / roles / attendees_only`.
