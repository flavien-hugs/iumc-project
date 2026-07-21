# ADR-0011 : Recherche — full-text search PostgreSQL

**Date :** 2026-07-17
**Statut :** Proposé

## Contexte

Le CDC (section 7.2) prévoit un moteur de recherche permettant de retrouver un service, un article, une FAQ ou une implantation. Le volume de contenu attendu au MVP est modeste (quelques dizaines de services et d'implantations, un nombre croissant mais limité d'articles). Aucune solution n'était précisée dans les documents source.

## Décision

La recherche sera implémentée via le **full-text search natif de PostgreSQL** (colonnes `tsvector` générées, index GIN) sur les champs pertinents des tables `service`, `article`, `faq` et `implantation`, exposée via un endpoint FastAPI unique de recherche transverse.

## Alternatives envisagées

- **Meilisearch ou Typesense** — offrent une meilleure tolérance aux fautes de frappe et une pertinence plus fine dès la sortie de boîte, ainsi qu'un support plus naturel du multilingue. Écartés pour le MVP : ajoutent un service supplémentaire à opérer et sauvegarder, disproportionné pour un volume de contenu aussi restreint. Solution de repli documentée si le volume de contenu ou les exigences de pertinence augmentent, notamment lors de l'ouverture au multilingue (CDC 7.6).
- **Elasticsearch/OpenSearch** — écarté d'emblée : complexité opérationnelle nettement supérieure au besoin, réservé à des volumes ou des besoins d'analyse bien plus importants.
- **Recherche côté client (filtrage JS sur un jeu de données préchargé)** — écarté : ne s'adapte pas à la croissance du contenu (articles, implantations supplémentaires au fil des ouvertures d'agence) et duplique la logique de filtrage déjà nécessaire côté API.

## Conséquences

- Aucune infrastructure supplémentaire ; s'appuie sur la base de données déjà en place ([ADR-0004](./0004-base-de-donnees-postgresql.md)).
- Pertinence et tolérance aux fautes de frappe plus limitées qu'avec un moteur dédié — acceptable au regard du volume de contenu attendu au MVP.
- Le passage à un moteur dédié (Meilisearch en priorité) devra être réévalué si le nombre d'implantations/services croît fortement (expansion territoriale prévue par le PRD) ou si le multilingue est activé.
