# ADR-0013 : Monorepo frontend — apps website/admin et packages partagés

**Date :** 2026-07-17
**Statut :** Accepté

## Contexte

Le frontend était une seule application SvelteKit portant à la fois le site public (`routes/[lang=lang]/(public)`) et le panel d'administration (`routes/admin`). Les deux surfaces divergent de plus en plus : le site public est SSR/SEO avec contenu éditorial, le panel est une application CSR authentifiée appelée à grossir fortement (demandes, contenus, utilisateurs, paramètres — PRD section 11). Elles partagent en revanche un même système de design (tokens, polices, composants de formulaire) et un même client API.

## Décision

Le dossier `frontend/` devient un **monorepo npm workspaces** :

```
frontend/
  apps/
    website/   → site public SvelteKit (SSR, port dev 5173)
    admin/     → panel d'administration SvelteKit (CSR, port dev 5174, routes sous /admin)
  packages/
    ui/        → @iumc/ui : tokens Tailwind (@theme), polices auto-hébergées,
                 composants de formulaire (TextField, SearchSelect, etc.)
    api/       → @iumc/api : client HTTP (appelApi, ErreurApi, API_BASE)
```

Les packages sont livrés **en source** (pas de build intermédiaire) : chaque app les compile via son propre pipeline Vite/SvelteKit. Le CSS du package `ui` déclare `@source` pour que Tailwind détecte les classes utilisées dans ses composants.

## Alternatives envisagées

- **Conserver une seule app avec groupes de routes** — fonctionne aujourd'hui, mais couple les cycles de vie : chaque évolution du panel rebuild et redéploie le site public (et inversement), et les dépendances spécifiques à l'un alourdissent l'autre. Écarté au profit de déploiements et périmètres indépendants.
- **Deux dépôts/dossiers totalement séparés** — écarté : dupliquerait le système de design et le client API, en contradiction avec la cohérence visuelle stricte du projet (un seul accent or, mêmes composants de formulaire).
- **pnpm/turborepo** — outillage plus riche mais dépendances supplémentaires ; npm workspaces suffit à cette échelle. Réévaluable si le nombre de packages croît.

## Conséquences

- Deux artefacts de déploiement : Nginx route `/admin` vers l'app admin et le reste vers le site public (deux services dans Docker Compose).
- L'app admin conserve ses routes sous le préfixe `/admin` (plutôt qu'un `paths.base`) pour que les liens internes existants restent valides et que le routage Nginx reste trivial.
- Toute nouvelle brique partagée (composant, utilitaire) doit aller dans `packages/` plutôt qu'être dupliquée entre apps.
- Les slugs pôles/services et le contenu éditorial restent dans `apps/website` (spécifiques au site public) ; ils devront à terme être servis par l'API plutôt que codés en dur.
