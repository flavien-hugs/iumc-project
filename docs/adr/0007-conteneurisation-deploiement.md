# ADR-0007 : Conteneurisation et déploiement — Docker Compose + Nginx

**Date :** 2026-07-17
**Statut :** Accepté

## Contexte

Le PRD (section 17.6) et le CDC (section 12.1) demandent Docker, Docker Compose, un serveur Nginx, un certificat SSL, des sauvegardes automatisées, et trois environnements (développement, préproduction, production). La disponibilité mensuelle cible est de 99 % (PRD section 13.2).

## Décision

Le projet sera conteneurisé avec **Docker**, orchestré via **Docker Compose** (un fichier compose par environnement : dev, préproduction, production), avec **Nginx** en reverse proxy/terminaison SSL devant les services SvelteKit (Node adapter) et FastAPI.

## Alternatives envisagées

- **Kubernetes** — écarté pour le MVP : complexité opérationnelle disproportionnée pour un site vitrine avec un seul serveur cible ; à reconsidérer si la charge ou le besoin de haute disponibilité multi-nœuds augmente significativement.
- **Déploiement sans conteneurs (PM2 + venv direct sur le serveur)** — écarté : moins reproductible entre environnements, complique la parité dev/préprod/prod explicitement demandée par les docs.

## Conséquences

- Un seul serveur Linux peut héberger l'ensemble de la stack (Nginx, SvelteKit, FastAPI, PostgreSQL, Redis) pour le MVP, simplifiant l'hébergement initial.
- Nginx gère la terminaison SSL (certificat Let's Encrypt) et le reverse proxy vers les conteneurs applicatifs.
- Les sauvegardes (base de données + volume de médias) doivent être scriptées et planifiées (cron ou tâche Celery Beat) dès la mise en place de l'environnement de production.
- La séparation dev/préproduction/production implique des fichiers `docker-compose.override.yml` ou équivalents par environnement, à définir lors du scaffolding.
