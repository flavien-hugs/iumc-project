# ADR-0001 : Organisation du dépôt en monorepo

**Date :** 2026-07-17
**Statut :** Proposé

## Contexte

Le projet comprend un frontend SvelteKit (site public + panel admin) et un backend FastAPI, déployés ensemble via Docker Compose ([ADR-0007](./0007-conteneurisation-deploiement.md)), avec une seule équipe technique aux premières phases. Aucune décision explicite n'a encore été prise sur l'organisation des dépôts source.

## Décision

Le code sera organisé en **un seul dépôt (monorepo)**, avec une structure de premier niveau du type :

```
/frontend   → application SvelteKit
/backend    → application FastAPI
/infra      → docker-compose, configuration Nginx, scripts de déploiement
/docs       → PRD, CDC, ADR
```

## Alternatives envisagées

- **Polyrepo (un dépôt par service)** — écarté pour le MVP: complique la coordination des changements transverses (ex. évolution d'un contrat d'API touchant frontend et backend simultanément) et multiplie les pipelines CI à maintenir pour une équipe réduite. À reconsidérer si des équipes distinctes prennent en charge frontend et backend indépendamment.

## Conséquences

- Un seul historique Git facilite le suivi des changements liés (API + consommation frontend dans le même commit/PR si pertinent).
- Nécessite une convention claire de CI (jobs séparés par dossier `frontend/` et `backend/` pour éviter de tout rebuilder à chaque commit).
- À valider avant le scaffolding : ce choix n'a pas été explicitement discuté avec l'utilisateur.
