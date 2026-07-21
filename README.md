# IUMC — Plateforme web

Site vitrine et panel d'administration d'**Ivoire Univers Multiservices et Commerces** (IUMC), entreprise ivoirienne de services juridiques, fonciers, immobiliers et industriels.

## Stack

| Domaine | Choix | ADR |
|---|---|---|
| Frontend | SvelteKit 5 + TypeScript + Tailwind v4, monorepo npm workspaces | [0002](docs/adr/0002-frontend-sveltekit.md), [0013](docs/adr/0013-monorepo-frontend.md) |
| Backend | FastAPI + SQLAlchemy 2.0 (async) + Alembic, architecture modulaire | [0003](docs/adr/0003-backend-fastapi.md), [0014](docs/adr/0014-backend-modulaire.md) |
| Base de données | PostgreSQL | [0004](docs/adr/0004-base-de-donnees-postgresql.md) |
| Tâches asynchrones | Celery + Redis | [0005](docs/adr/0005-taches-asynchrones-celery-redis.md) |
| Déploiement | Docker Compose + Nginx | [0007](docs/adr/0007-conteneurisation-deploiement.md) |
| Notifications | Server-Sent Events + Redis Pub/Sub | [0016](docs/adr/0016-notifications-sse.md) |

L'ensemble des décisions d'architecture est documenté dans [`docs/adr/`](docs/adr/README.md) ; le contexte produit dans [`docs/prd.md`](docs/prd.md) et [`docs/cdc-fonctionnel.md`](docs/cdc-fonctionnel.md).

## Structure du dépôt

```
backend/            API FastAPI (app/core, app/modules/<domaine>, migrations Alembic)
frontend/
  apps/website/      Site public (SSR)
  apps/admin/         Panel d'administration (CSR)
  packages/ui/        Design system partagé (composants, styles, polices)
  packages/api/        Client HTTP partagé vers l'API
infra/               docker-compose.yml (dev) + docker-compose.prod.yml (+ Nginx/TLS)
docs/                PRD, CDC fonctionnel, ADR
```

## Démarrage

Prérequis : Docker et Docker Compose.

```bash
cp backend/.env.example backend/.env      # ajuster si besoin (secrets de dev fournis par défaut)
make up                                    # construit et démarre toute la stack
make migrate                               # applique les migrations de base de données
make seed                                  # peuple un super admin + données de démonstration
```

Une fois démarré :

- Site public : http://localhost:3000
- Panel admin : http://localhost:3001/admin
- API (docs interactives) : http://localhost:8000/docs

Identifiants de connexion par défaut (dev uniquement, voir `backend/app/seed.py`) : `admin@iumc.ci` / `ChangerMoi!2026` (ou la valeur de `SEED_ADMIN_PASSWORD` si définie).

Toutes les cibles disponibles : `make help`.

## Développement

Le rechargement à chaud du frontend n'est pas disponible dans les conteneurs de dev (images de production, cf. optimisation des Dockerfiles) : pour itérer sur le site ou le panel, lancez-les hors Docker pendant que `make up` fournit l'API, PostgreSQL et Redis :

```bash
make frontend-install
make frontend-dev-website   # http://localhost:5173
make frontend-dev-admin     # http://localhost:5174
```

Vérifications avant commit :

```bash
make frontend-check   # svelte-check (site + panel)
make backend-lint     # ruff
```

## Production

```bash
make prod-up
```

Utilise `infra/docker-compose.prod.yml` en surcouche : Nginx expose seul les ports 80/443 (TLS via Let's Encrypt, certificat à renseigner dans `infra/nginx/nginx.conf`), les autres services ne sont plus exposés directement à l'hôte.
