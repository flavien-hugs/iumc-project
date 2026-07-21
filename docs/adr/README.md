# Architecture Decision Records (ADR)

Ce dossier contient les décisions d'architecture structurantes du projet IUMC.

## Format

Chaque ADR suit le gabarit défini dans [`template.md`](./template.md) :

- **Contexte** — le problème ou la question à trancher ;
- **Décision** — le choix retenu ;
- **Alternatives envisagées** — les options écartées et pourquoi ;
- **Conséquences** — impacts positifs et négatifs, points de vigilance.

## Statuts

- `Proposé` — décision suggérée, en attente de validation par IUMC ou l'équipe technique ;
- `Accepté` — décision validée, à appliquer ;
- `Remplacé` — décision remplacée par un ADR ultérieur (indiquer lequel) ;
- `Obsolète` — décision abandonnée sans remplacement.

## Index

| ADR | Titre | Statut |
|-----|-------|--------|
| [0001](./0001-repertoire-monorepo.md) | Organisation du dépôt en monorepo | Proposé |
| [0002](./0002-frontend-sveltekit.md) | Choix du framework frontend — SvelteKit | Accepté |
| [0003](./0003-backend-fastapi.md) | Choix du framework backend — FastAPI | Accepté |
| [0004](./0004-base-de-donnees-postgresql.md) | Choix de la base de données — PostgreSQL | Accepté |
| [0005](./0005-taches-asynchrones-celery-redis.md) | Traitement asynchrone — Celery + Redis | Proposé |
| [0006](./0006-stockage-medias.md) | Stockage des médias — local puis S3/MinIO | Accepté |
| [0007](./0007-conteneurisation-deploiement.md) | Conteneurisation et déploiement — Docker Compose + Nginx | Accepté |
| [0008](./0008-authentification-panel-admin.md) | Authentification du panel — JWT en cookie httpOnly | Proposé |
| [0009](./0009-strategie-rendu-sveltekit.md) | Stratégie de rendu — SSR public / CSR panel | Proposé |
| [0010](./0010-notifications-in-app.md) | Notifications dans le panel — polling léger sur table dédiée | Remplacé par [0016](./0016-notifications-sse.md) |
| [0011](./0011-recherche-full-text-postgresql.md) | Recherche — full-text search PostgreSQL | Proposé |
| [0012](./0012-reinitialisation-mdp-limitation-tentatives.md) | Réinitialisation de mot de passe et limitation des tentatives | Proposé |
| [0013](./0013-monorepo-frontend.md) | Monorepo frontend — apps website/admin et packages partagés | Accepté |
| [0014](./0014-backend-modulaire.md) | Architecture backend modulaire par domaine métier | Accepté |
| [0015](./0015-nommage-anglais.md) | Convention de nommage : code en anglais, contenu en français | Accepté |
| [0016](./0016-notifications-sse.md) | Notifications dans le panel — Server-Sent Events | Accepté |

Les ADR marqués « Accepté » reprennent des choix déjà validés dans la conversation de cadrage. Les ADR « Proposé » couvrent des décisions techniques dérivées, nécessaires au scaffolding, mais qui n'ont pas encore été explicitement discutées — à valider avant de démarrer le développement correspondant.

## Couverture des exigences fonctionnelles du PRD

Vérification croisée avec le PRD/CDC lors de la rédaction des ADR 0010 à 0012 : les décisions ci-dessus couvrent désormais les exigences fonctionnelles structurantes ayant un impact d'architecture (auth, stockage, async, rendu, notifications, recherche). Restent volontairement traités comme des détails d'implémentation plutôt que des ADR séparés, documentés en note dans l'ADR le plus pertinent :

- contrôle de format/taille des fichiers téléversés → note dans [0006](./0006-stockage-medias.md) ;
- génération SEO (sitemap, robots.txt, Open Graph, données structurées) et architecture multilingue future → notes dans [0009](./0009-strategie-rendu-sveltekit.md).

Le **modèle de permissions par rôle** (section 12 du PRD — 5 rôles, portée des accès) n'est couvert par aucun ADR : il s'agit d'un modèle de données/autorisation à documenter lors de la conception du schéma de base de données plutôt qu'une décision d'architecture technique.
