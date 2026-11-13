# Fonctionnel — ce que l'on peut faire dans Clakettes

[ES](../es/FUNCIONAL.md) · [EN](../en/FUNCIONAL.md) · [FR](FUNCIONAL.md) · [DE](../de/FUNCIONAL.md) · [IT](../it/FUNCIONAL.md) · [CA](../ca/FUNCIONAL.md) · [EU](../eu/FUNCIONAL.md) · [GL](../gl/FUNCIONAL.md) · [OC](../oc/FUNCIONAL.md)

Valeur réelle du projet par rôle, avec le flux qui le soutient. Détail opérationnel dans [USO.md](USO.md), référence des endpoints dans [API.md](API.md).

## Festival (organizer)

1. Créez le festival (`POST /api/festivals/`) avec description, site web, lieu et logo.
2. Ouvrez des appels : formulaires d'inscription avec sections, rôles et étiquettes (`RegistrationForm + Sections + Links`), exposés par lien public que quiconque peut remplir sans compte.
3. Recevez des courts-métrages liés à vos appels et localisations de tournage.
4. Montez la programmation : événements (gala, projection, atelier, table ronde, réseautage, récompenses, fête, masterclass, Q&A) avec types de billets, sièges (disponible/réservé/vendu/assigné/bloqué), réservations et check-in des participants ; exportez les participants vers CSV et les événements vers ICS. Filtrez chaque œuvre lors du visionnage avec état `pending/screened/disqualified` et motif, filtrez par état, disqualifiées ou étiquette de participant. L'organisation vérifie les étiquettes d'éligibilité des participants (résident, étudiant) par méthodes externes, et le participant peut demander la vérification en joignant un certificat de résidence ou d'inscription.
5. Nommez des comités avec membres et publiez des récompenses (vérifiées ou non, publiques ou non) par festival, court-métrage ou utilisateur, avec étiquettes d'éligibilité et vérification du récipiendaire.
6. Communiquez : canaux du festival (admin/moderator/member), messages et images sur le profil, livrets de règles.

Seul édite/supprime ses propres festivals et gère ses utilisateurs (`require_festival_admin`). Les membres se joignent automatiquement comme `attendee` ; les autres rôles sont assignés par un admin (409 si déjà membre).

## Professionnel (utilisateur, jury, autres métiers)

- Profil avec métier (réalisation, interprétation, son, scénario, montage, costume, maquillage, figuration, doublage, foley, presse, production, distribution…), bio et palmarès lié à des festivals de la plateforme ou externe par lien.
- Confidentialité champ par champ (email, bio, localisation) et profils publics/privés.
- Chaque utilisateur édite son profil et ses courts-métrages ; le jury consulte et vote selon son festival.
- Chat direct et de groupe/canal avec chiffrement de bout en bout : les clés publiques sont publiées à `POST /api/users/me/public-key`, le serveur stocke et retransmet seulement le chiffrement, le vrai chiffrement se fait dans l'app.

## Équipe express (attendee)

- Auto-join au festival (`POST /api/festivals/{id}/join`, rôle `attendee`) et sortie libre (`leave`).
- Géolocalisez les participants, coordonnez le groupe par chat et présentez votre court-métrage au concours express.
- Réservez un siège aux événements et envoyez des inscriptions par lien public (états : en attente/approuvée/rejetée/en liste d'attente/annulée ; paiements : impayé/en attente/payé/remboursé/annulé).

## Public

Découvrez les festivals (`GET /api/festivals/` paginé et public), suivez les courts-métrages et les palmarès, contactez par chat et consultez les lieux sur la carte.

## Administrateur global (admin)

Voit et édite tout (utilisateurs, festivals, courts-métrages, canaux, formulaires). Opérations dans [ADMINISTRACION.md](ADMINISTRACION.md) (stats, tables, reset, sauvegardes, secrets).

## Jury (juror)

- Consulte les œuvres assignées à son festival et émet des votes par court-métrage (`POST /api/jury-votes/`).
- Notation par œuvre avec agrégation automatique ; anonymat optionnel.
- Consulte les résultats agrégés pour les organisateurs.

## États à connaître

- Membre de festival : `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Inscription : `draft → submitted → approved / rejected` ; soumission : `pending / approved / rejected / waitlisted / cancelled`.
- Participant à un événement : `registered / attended / no_show / cancelled`.
- Sélection en projection : `pending / screened / disqualified`.
- Notes du jury et procès-verbaux par œuvre, avec annotation : `special_mention / accesit / other`.
- Vérification d'étiquette de participant : `unverified / pending / verified / rejected`.
- Portée de visibilité des événements : `public / festival_members / roles / attendees_only`.

## Voir aussi

- [USO.md](USO.md) : démarrage et opération du système
- [API.md](API.md) : référence des endpoints
- [ADMINISTRACION.md](ADMINISTRACION.md) : administration du déploiement