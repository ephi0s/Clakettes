# Fonctionnel — ce qu'on peut faire dans Clakettes

[ES](../es/FUNCIONAL.md) · [EN](../en/FUNCIONAL.md) · [FR](FUNCIONAL.md) · [DE](../de/FUNCIONAL.md) · [IT](../it/FUNCIONAL.md) · [CA](../ca/FUNCIONAL.md) · [EU](../eu/FUNCIONAL.md) · [GL](../gl/FUNCIONAL.md) · [OC](../oc/FUNCIONAL.md)

Utilité réelle du projet par rôle, avec le flux qui la soutient. Détail opérationnel dans [USO.md](USO.md), référence d'endpoints dans [API.md](../es/API.md).

## Festival (organizer)

1. Crée le festival (`POST /api/festivals/`) avec description, web, siège et logo.
2. Ouvre des appels : formulaires d'inscription avec sections, rôles et étiquettes (`RegistrationForm + Sections + Links`), exposés par lien public que quiconque peut remplir sans compte.
3. Reçoit des courts liés à tes appels et localisations de tournage.
4. Monte la programmation : événements (gala, projection, atelier, table, networking, prix, fête, masterclass, Q&A) avec types d'entrée, sièges (disponible/réservée/vendue/assignée/bloquée), réservations et check-in des participants ; exporte participants en CSV et événements en ICS. Criblage de chaque film de la projection : statut `pending/screened/disqualified` avec motif, et filtres par statut, films disqualifiés ou étiquette de participant. L'organisation vérifie les étiquettes d'éligibilité (résident, étudiant) par des méthodes externes, et le participant peut demander la vérification en joignant un certificat de résidence ou une carte d'étudiant.
5. Nomme des comités avec membres et publie des prix (vérifiés ou non, publics ou non) par festival, court ou utilisateur, avec étiquettes d'éligibilité et vérification du bénéficiaire.
6. Communique : canaux du festival (admin/moderator/member), messages et images dans le profil, rulebooks.

Édite/supprime uniquement ses festivals et gère ses utilisateurs (`require_festival_admin`). Les membres se joignent seuls comme `attendee` ; le reste des rôles est assigné par un admin (409 si déjà membre).

## Professionnel (user, jury, reste des métiers)

- Profil avec métier (réalisation, interprétation, son, scénario, montage, costumes, maquillage, figuration, doublage, foley, presse, production, distribution…), bio et palmarès lié aux festivals de la plateforme ou externe par lien.
- Confidentialité champ par champ (email, bio, localisation) et profils publics/privés.
- Chaque utilisateur édite son profil et ses courts ; le jury consulte et vote selon son festival.
- Chat direct et de groupe/canal avec chiffrement de bout en bout : les clés publiques se publient sur `POST /api/users/me/public-key`, le serveur ne fait que garder et retransmettre chiffré, le chiffrement réel a lieu dans l'app.

## Équipe express (attendee)

- Auto-join au festival (`POST /api/festivals/{id}/join`, rôle `attendee`) et sortie libre (`leave`).
- Géolocalise participants, coordonne le groupe par chat et présente le court au concours express.
- Réserve siège en événements et envoie inscriptions par lien public (états : pendiente/aprobada/rechazada/en espera/cancelada ; paiements : impagado/pendiente/pagado/reembolsado/cancelado).

## Public

Découvre festivals (`GET /api/festivals/` paginé et public), suit courts et palmarès, contacte par chat et consulte sièges sur la carte.

## Administrateur global (admin)

Voit et édite tout (utilisateurs, festivals, courts, canaux, formulaires). Opérationnelle dans [ADMINISTRACION.md](ADMINISTRACION.md) (stats, tables, reset, backups, secrets).

## États à connaître

- Membre de festival : `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Inscription : `draft → submitted → approved / rejected` ; envoi : `pending / approved / rejected / waitlisted / cancelled`.
- Participant à événement : `registered / attended / no_show / cancelled`.
- Criblage en projection : `pending / screened / disqualified`.
- Notes du jury et procès-verbaux par œuvre, avec annotation : `special_mention / accesit / other`.
- Vérification d'étiquette de participant : `unverified / pending / verified / rejected`.
- Portée de visibilité d'événements : `public / festival_members / roles / attendees_only`.
