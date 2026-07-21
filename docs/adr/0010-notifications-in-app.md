# ADR-0010 : Notifications dans le panel — polling léger sur table dédiée

**Date :** 2026-07-17
**Statut :** Remplacé par [ADR-0016](./0016-notifications-sse.md)

## Contexte

Le PRD (section 19) et le CDC (section 9) prévoient des notifications pour une nouvelle demande, une affectation, un changement de statut et les événements de rendez-vous, livrées à la fois par e-mail et **dans le panel** (« notification dans le panel » — canal explicitement distinct de l'e-mail). Ce canal in-app n'est couvert par aucune décision actuelle : [ADR-0005](./0005-taches-asynchrones-celery-redis.md) ne traite que l'envoi asynchrone (e-mails, exports), pas la livraison d'un signal à l'interface du panel.

Le volume attendu est faible pour le MVP (une poignée d'administrateurs/agents connectés simultanément, quelques dizaines de demandes par mois au démarrage).

## Décision

Les notifications in-app seront **persistées dans une table PostgreSQL dédiée** (`notification`, liée à un utilisateur et à une ressource), écrites de manière synchrone au moment de l'événement métier (nouvelle demande, affectation, changement de statut, rendez-vous). Le panel SvelteKit les récupère par **polling léger** (requête périodique, ex. toutes les 30 à 60 secondes) sur un endpoint FastAPI dédié, plutôt que par une connexion persistante.

## Alternatives envisagées

- **WebSocket (FastAPI natif ou Socket.io)** — offre une livraison temps réel, écarté pour le MVP : complexité d'infrastructure (gestion de connexions persistantes, reconnexion, scalabilité horizontale) disproportionnée face à un besoin de fraîcheur de l'ordre de la minute, pour un nombre d'utilisateurs internes réduit.
- **Server-Sent Events (SSE)** — plus simple que WebSocket mais maintient tout de même une connexion ouverte par client ; écarté pour la même raison de complexité non justifiée au MVP.
- **Notifications uniquement par e-mail (pas de canal in-app)** — écarté : contraire à l'exigence explicite des docs de distinguer les deux canaux, et moins adapté à un usage interne fréquent (un agent ne consulte pas nécessairement ses e-mails en continu pendant qu'il travaille dans le panel).

## Conséquences

- Aucune infrastructure supplémentaire : réutilise PostgreSQL et l'API REST existante.
- Latence de livraison bornée par l'intervalle de polling (acceptable pour ce volume, à documenter comme limite connue).
- La table `notification` doit prévoir un statut lu/non lu et un lien vers la ressource concernée (demande, rendez-vous) pour permettre la navigation directe depuis le panel.
- Si le nombre d'utilisateurs simultanés ou l'exigence de fraîcheur augmente significativement (post-MVP), une migration vers WebSocket reste possible sans changer le modèle de données des notifications.
