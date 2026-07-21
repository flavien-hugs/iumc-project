# ADR-0003 : Choix du framework backend — FastAPI

**Date :** 2026-07-17
**Statut :** Accepté

## Contexte

Le PRD (section 17.2) proposait FastAPI ou Django ; le CDC (section 12.1) proposait Python + FastAPI ou Django avec une API REST sécurisée. Le backend doit exposer une API REST pour un frontend découplé (SvelteKit), gérer l'authentification par rôles (5 rôles, section 8.12 du CDC), la validation stricte des entrées (formulaires publics, section 13), et s'intégrer avec Celery pour les tâches asynchrones (notifications e-mail, exports).

## Décision

Le backend sera développé avec **FastAPI** (Python), exposant une API REST versionnée, avec validation des schémas via Pydantic.

## Alternatives envisagées

- **Django (+ Django REST Framework)** — offre un admin auto-généré et un ORM mature, ce qui aurait pu accélérer le panel d'administration. Écarté car le projet nécessite une API découplée pour un frontend SvelteKit plutôt qu'un rendu de templates côté serveur, et FastAPI offre de meilleures performances asynchrones natives ainsi qu'une validation de schéma plus légère, utile pour les nombreux formulaires publics du site.
- **Node.js (NestJS/Express)** — écarté pour rester sur un unique écosystème Python côté serveur, cohérent avec Celery et simplifiant l'équipe technique.

## Conséquences

- Validation des entrées centralisée et typée via Pydantic, réduisant le risque d'injection et de données malformées (exigence sécurité section 14 du CDC).
- Pas d'interface d'administration auto-générée comme Django Admin : le panel devra être développé entièrement côté SvelteKit + API, ce qui représente plus de développement initial mais un contrôle total sur l'UX du panel (cohérent avec les besoins spécifiques par rôle, section 12 du PRD).
- Compatible nativement avec Celery pour les tâches asynchrones (envoi d'e-mails, exports, notifications).
- Nécessite de choisir/mettre en place un ORM (SQLAlchemy ou équivalent) et un outil de migration (Alembic), à documenter dans un ADR ultérieur si besoin lors du scaffolding.
