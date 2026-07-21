# ADR-0009 : Stratégie de rendu — SSR public / CSR panel

**Date :** 2026-07-17
**Statut :** Proposé

## Contexte

Le site public a une exigence SEO forte (référencement naturel, PRD section 16 ; recherches locales ciblées, CDC section 10) et doit afficher son contenu principal sans connexion (PRD section 10.1). Le panel d'administration est un espace applicatif derrière authentification, sans enjeu SEO, où la réactivité de l'interface (filtres, tableaux, formulaires) prime.

## Décision

Le site public utilisera le **rendu côté serveur (SSR) de SvelteKit** pour toutes les pages indexables (accueil, présentation, pôles, services, implantations, actualités, FAQ, contact). Le panel d'administration utilisera un **rendu principalement côté client (CSR)** après un premier chargement authentifié, les données étant chargées via l'API FastAPI.

## Alternatives envisagées

- **SSG (Static Site Generation) pour le site public** — envisageable pour les pages peu volatiles (mentions légales, présentation), mais écarté comme stratégie par défaut car les contenus (services, implantations, actualités) sont administrables et doivent refléter les changements sans étape de rebuild manuelle. Pourra être appliqué ponctuellement page par page si la fraîcheur du contenu le permet et que la performance le justifie.
- **SSR complet pour le panel également** — écarté : n'apporte pas de bénéfice SEO derrière authentification et complexifie inutilement la gestion d'état des interactions riches (filtres, tableaux paginés).

## Conséquences

- Deux modes de rendu coexistent dans la même application SvelteKit ; la séparation doit être clairement établie par convention de dossiers dès le scaffolding : `routes/[lang=lang]/(public)` pour le site public (SSR), `routes/admin` pour le panel (CSR, `ssr = false`). Le panel est placé sous un segment de chemin réel (`/admin`) plutôt qu'un groupe de routes seul, car un groupe de routes n'ajoute pas de segment d'URL et entre en conflit avec la racine `/` gérée par le site public.
- Le SSR public implique que le serveur Node de SvelteKit doit pouvoir joindre l'API FastAPI à chaque requête de page — à prendre en compte dans la configuration réseau Docker Compose ([ADR-0007](./0007-conteneurisation-deploiement.md)).
- Une stratégie de cache HTTP (ou ISR-like via SvelteKit) pourra être ajoutée ultérieurement sur les pages publiques à fort trafic si la charge sur l'API le justifie.
- Le SSR facilite directement deux exigences distinctes du PRD non détaillées par ailleurs : l'**aperçu de partage social** (balises Open Graph par page, section 16) et la génération de **sitemap XML, robots.txt et données structurées** (section 16) via des endpoints serveur SvelteKit dédiés (`+server.ts`) plutôt qu'un service séparé.
- L'**architecture multilingue future** (CDC section 7.6 : ajout ultérieur de l'anglais et de langues locales) doit être anticipée dès le scaffolding par une convention de routes préfixées par langue (ex. `routes/[lang]/(public)`) même si seul le français est livré au MVP, afin d'éviter une réécriture complète du routage lors de l'ouverture au multilingue.
- À valider avant l'implémentation : ce choix n'a pas été explicitement discuté avec l'utilisateur.
