# ADR-0004 : Choix de la base de données — PostgreSQL

**Date :** 2026-07-17
**Statut :** Accepté

## Contexte

Le PRD (section 17.3) et le CDC (section 12.1) recommandent PostgreSQL. Le modèle de données (PRD section 18) comporte des entités relationnelles classiques (utilisateurs, pôles, services, implantations, demandes, rendez-vous, articles, FAQ, journal d'activité) avec des relations claires (un service appartient à un pôle, une demande référence un pôle/service/implantation/agent). Les besoins de filtrage et de statistiques (répartition par pôle, par ville, évolution mensuelle) impliquent des requêtes agrégées.

## Décision

La base de données sera **PostgreSQL**.

## Alternatives envisagées

- **MySQL/MariaDB** — équivalent fonctionnel pour ce périmètre, écarté sans avantage particulier face à PostgreSQL, qui offre un typage plus riche (JSONB pour les champs semi-structurés comme les FAQ par service ou les étapes d'accompagnement) et un meilleur support des index avancés pour les futures recherches géographiques (implantations avec coordonnées GPS).
- **MongoDB / NoSQL** — écarté : le modèle de données est fortement relationnel (statuts, historiques, permissions par rôle), ce qui se prête mal à un stockage document sans jointures natives.

## Conséquences

- Support natif de PostGIS envisageable plus tard si la carte des implantations évolue vers des requêtes géospatiales avancées.
- Types JSONB disponibles pour les champs flexibles (étapes, documents nécessaires, FAQ liées) sans multiplier les tables de jointure pour du contenu semi-structuré.
- Nécessite un outil de migration de schéma (Alembic, cohérent avec FastAPI/SQLAlchemy — voir [ADR-0003](./0003-backend-fastapi.md)).
