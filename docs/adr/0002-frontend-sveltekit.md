# ADR-0002 : Choix du framework frontend — SvelteKit

**Date :** 2026-07-17
**Statut :** Accepté

## Contexte

Le PRD (section 17.1) et le CDC (section 12.1) recommandaient initialement Next.js + TypeScript + Tailwind pour le frontend, avec un impératif fort de rendu optimisé pour le référencement (site vitrine destiné à être trouvé sur des requêtes locales : « accompagnement foncier à Bouaké », etc. — CDC section 10).

Le site public doit être administrable, rapide sur mobile (CDC section 14 : affichage < 3 s sur connexion mobile correcte), et responsive. Le panel d'administration est un espace applicatif distinct, derrière authentification, sans contrainte SEO.

## Décision

Le frontend sera développé avec **SvelteKit + TypeScript + Tailwind CSS**, pour le site public comme pour le panel d'administration (un seul projet SvelteKit, avec séparation logique des routes).

## Alternatives envisagées

- **Next.js (React)** — recommandation initiale des docs. Écosystème plus large, plus de développeurs disponibles en sous-traitance. Écarté au profit de SvelteKit pour un bundle plus léger et un modèle de réactivité plus simple, jugés préférables sur un site orienté performance mobile et sans besoin d'un écosystème React spécifique (pas de composants tiers React requis).
- **Nuxt (Vue)** — alternative de poids comparable, écartée sans raison technique forte contre SvelteKit ; SvelteKit retenu par préférence de l'équipe.

## Conséquences

- Bundle JS plus léger que Next.js à fonctionnalité équivalente, cohérent avec l'objectif de performance mobile.
- Écosystème de composants tiers plus restreint qu'avec React ; certains composants (carte interactive, éditeur riche pour les articles) devront être intégrés via des libs agnostiques JS ou des équivalents Svelte natifs.
- Marché de développeurs SvelteKit plus réduit que Next.js en cas de recrutement ou sous-traitance future — point de vigilance si l'équipe change.
- SSR natif de SvelteKit couvre l'exigence SEO sans configuration supplémentaire lourde (voir [ADR-0009](./0009-strategie-rendu-sveltekit.md) pour la stratégie de rendu détaillée).
