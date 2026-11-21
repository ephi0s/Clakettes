# Fonctionnel — ce qu'on peut faire dans Clakettes

[ES](../es/FUNCIONAL.md) · [EN](../en/FUNCIONAL.md) · [FR](FUNCIONAL.md) · [DE](../de/FUNCIONAL.md) · [IT](../it/FUNCIONAL.md) · [CA](../ca/FUNCIONAL.md) · [EU](../eu/FUNCIONAL.md) · [GL](../gl/FUNCIONAL.md) · [OC](../oc/FUNCIONAL.md)

Utilité réelle du projet par rôle, avec le flux qui la soutient. Détail opérationnel dans [USO.md](USO.md), référence des endpoints dans [API.md](API.md).

## Festival (organisateur)

1. Crée le festival (`POST /api/festivals/`) avec description, site web, lieu et logo.
2. Ouvre des appels : formulaires d'inscription avec sections, rôles et étiquettes (`RegistrationForm + Sections + Links`), exposés par lien public que tout le monde peut remplir sans compte.
3. Reçoit les courts liés à vos appels et les lieux de tournage.
4. Monte la programmation : événements (gala, projection, atelier, table, networking, prix, fête, masterclass, Q&A) avec types de billets, sièges (disponible/réservé/vendu/assigné/bloqué), réservations et check-in des participants ; exporte les participants en CSV et les événements en ICS. Crible chaque œuvre du visionnage avec statut `pending/screened/disqualified` et motif, et filtre par statut, disqualifiés ou étiquette de participant. L'organisation vérifie les étiquettes d'éligibilité (résident, étudiant) avec des méthodes externes, et le participant peut demander la vérification en joignant un certificat de résidence ou de scolarité.
5. Nomme des comités avec membres et publie des prix (vérifiés ou non, publics ou non) par festival, court ou utilisateur, avec étiquettes d'éligibilité et vérification du destinataire.
6. Communique : canaux du festival (admin/moderator/member), messages et images sur le profil, rulebooks.

Il ne modifie/supprime que ses festivals et gère ses utilisateurs (`require_festival_admin`). Les membres rejoignent seuls comme `attendee` ; les autres rôles sont assignés par un admin (409 si déjà membre).

## Professionnel (utilisateur, jury, autres métiers)

- Profil avec métier (réalisation, interprétation, son, scénario, montage, costumes, maquillage, figurant, doublage, foley, presse, production, distribution…), bio et palmarès liés aux festivals de la plateforme ou externes par lien.
- Confidentialité champ par champ (email, bio, localisation) et profils publics/privés.
- Chaque utilisateur modifie son profil et ses courts ; le jury consulte et vote selon son festival.
- Chat direct et de groupe/canal avec chiffrement de bout en bout : les clés publiques sont publiées sur `POST /api/users/me/public-key`, le serveur ne stocke et ne relaie que du chiffré, le vrai chiffrement a lieu dans l'application. Entre nœuds fédérés, le message passe par le bridge signé, est dédupliqué par `message_id` et trié par date ; vous pouvez signaler des messages et les administrateurs peuvent réduire au silence des utilisateurs ou filtrer des mots.

## Équipe express (attendee)

- Auto-join au festival (`POST /api/festivals/{id}/join`, rôle `attendee`) et sortie libre (`leave`).
- Géolocalise les participants, coordonne le groupe par chat et présente le court au concours express.
- Réserve un siège aux événements et envoie des inscriptions par lien public (états : en attente/approuvé/rejeté/listé d'attente/annulé ; paiements : impayé/en attente/payé/remboursé/annulé).

## Public

Découvre les festivals (`GET /api/festivals/` paginé et public), suit les courts et le palmarès, contacte par chat et consulte les lieux sur la carte.

## Administrateur global (admin)

Voit et modifie tout (utilisateurs, festivals, courts, canaux, formulaires). Exploitation dans [ADMINISTRACION.md](ADMINISTRACION.md) (stats, tables, reset, sauvegardes, secrets). En fédération, il enregistre les nœuds et leurs politiques (`import_only`, `disable_chat`, `disable_search`), exporte et importe des bundles, migre les festivals et les identités d'utilisateur avec leurs redirections, publie des événements, modère le chat et surveille la résilience (métriques p50/p95 et révocation de clés).

## Jury (juror)

- Consulte les œuvres assignées à son festival et vote par court (`POST /api/jury-votes/`).
- Notation par œuvre avec agrégation automatique ; anonymat optionnel.
- Consulte les résultats agrégés pour les organisateurs.

## États à connaître

- Membre de festival : `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Inscription : `draft → submitted → approved / rejected` ; envoi : `pending / approved / rejected / waitlisted / cancelled`.
- Participant à un événement : `registered / attended / no_show / cancelled`.
- Criblage en projection : `pending / screened / disqualified`.
- Notes du jury et procès-verbaux par œuvre, avec annotation : `special_mention / accesit / other`.
- Vérification de l'étiquette de participant : `unverified / pending / verified / rejected`.
- Portée de visibilité des événements : `public / festival_members / roles / attendees_only`.

## Voir aussi

- [USO.md](USO.md) : démarrage et exploitation du système
- [API.md](API.md) : référence des endpoints
- [ADMINISTRACION.md](ADMINISTRACION.md) : administration du déploiement
