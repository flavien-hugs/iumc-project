# ADR-0016 : Notifications dans le panel — Server-Sent Events

**Date :** 2026-07-20
**Statut :** Accepté

## Contexte

L'[ADR-0010](./0010-notifications-in-app.md) avait retenu un polling léger (30-60 s) sur `GET /admin/notifications`, en écartant explicitement le SSE pour le MVP (« complexité non justifiée »). Une demande explicite de livraison en temps réel via `EventSource`/SSE revient sur ce choix : latence perçue d'une minute jugée insuffisante pour un badge de notifications consulté en continu pendant le travail dans le panel.

Contrainte technique de départ, déjà favorable : Redis est une dépendance dure du projet depuis l'[ADR-0005](./0005-taches-asynchrones-celery-redis.md) (Celery, rate-limiting), avec un client async déjà partagé (`app/core/redis.py`). Le backend tourne aujourd'hui en un seul processus (pas de `--workers` dans `Dockerfile`, aucune des deux configurations Compose ne le change) — un mécanisme purement en mémoire aurait donc fonctionné tout aussi bien à l'instant présent, mais casserait silencieusement le jour où le nombre de workers augmenterait.

## Décision

Les notifications in-app restent stockées en base (table `notification`, inchangée), mais sont désormais poussées en direct via un abonnement **Redis Pub/Sub** relayé en **Server-Sent Events** :

- Chaque création de notification publie sur le canal `notifications:{user_id}` juste après le commit de la transaction qui l'a créée.
- Un nouvel endpoint `GET /admin/notifications/stream` s'abonne à ce canal et relaie chaque message au client via un flux `text/event-stream`, avec un battement (« heartbeat ») toutes les 15 secondes.
- Le panel ouvre une connexion `EventSource` par session (reconnexion automatique native du navigateur, aucun code de reconnexion à écrire) et la ferme explicitement au démontage du composant.
- `GET /admin/notifications` (désormais paginé) reste la source de vérité pour la resynchronisation initiale au chargement — le flux SSE ne pousse que les évènements postérieurs à son ouverture, il ne rejoue pas l'historique.
- Le pub/sub Redis (plutôt qu'un simple registre en mémoire du processus) garde le mécanisme correct si le backend passe un jour à plusieurs workers, pour un coût marginal aujourd'hui.

## Alternatives envisagées

- **Conserver le polling de l'ADR-0010** — écarté : ne répond pas à la demande explicite de livraison en temps réel.
- **WebSocket** — écarté pour les mêmes raisons qu'en 2010 : canal bidirectionnel non nécessaire ici (les notifications ne circulent que serveur→client), complexité de gestion de connexion plus élevée que le SSE pour un bénéfice nul dans ce sens unique.
- **Registre en mémoire du processus (sans Redis)** — écarté : fonctionnerait à l'identique tant qu'il n'y a qu'un seul worker, mais deviendrait silencieusement incorrect (notifications perdues pour les clients connectés à un autre worker) dès que ce ne serait plus le cas, sans qu'aucun signal n'alerte du problème.

## Conséquences

- Remplace l'ADR-0010, dont le statut passe à *Remplacé par ADR-0016* (voir aussi l'index `docs/adr/README.md`).
- Une connexion Redis Pub/Sub reste ouverte par onglet de panel connecté ; sans conséquence à l'échelle d'usage interne visée (une poignée d'administrateurs/agents), à surveiller si l'audience change d'échelle.
- Le cookie JWT n'est vérifié qu'à l'ouverture de la connexion SSE (pas de re-vérification par requête comme sur le reste de l'API) ; l'endpoint revérifie donc périodiquement (toutes les ~4 battements) que le compte est toujours actif et non supprimé, et coupe le flux sinon.
- Nginx doit désactiver le buffering et étendre le délai d'inactivité spécifiquement sur ce chemin, sans changer le comportement du reste de `/api/`.
