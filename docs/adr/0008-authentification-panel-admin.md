# ADR-0008 : Authentification du panel — JWT en cookie httpOnly

**Date :** 2026-07-17
**Statut :** Proposé

## Contexte

Le panel d'administration nécessite une authentification sécurisée avec gestion des rôles, expiration de session, contrôle des tentatives de connexion et journalisation des connexions (PRD section 11.1, CDC section 8.1). Le frontend (SvelteKit) et le backend (FastAPI) sont deux applications découplées communiquant via API REST, ce qui impose de choisir explicitement un mécanisme de propagation de l'identité entre les deux.

## Décision

L'authentification du panel utilisera des **JWT (access token courte durée + refresh token) stockés en cookies `httpOnly`, `Secure`, `SameSite=Strict`**, émis par FastAPI et vérifiés à chaque requête API. Le serveur SvelteKit (via ses `load`/`hooks` côté serveur) relaie les cookies au backend sans jamais exposer les tokens au JavaScript client.

## Alternatives envisagées

- **JWT en localStorage/sessionStorage côté client** — écarté : expose les tokens à un vol via XSS, contraire à l'exigence de protection contre les attaques XSS (PRD section 14).
- **Sessions serveur classiques (cookie de session + store Redis)** — alternative valable et plus simple à invalider immédiatement (déconnexion instantanée, révocation centralisée). Écartée au profit de JWT pour limiter les allers-retours vers un store de session à chaque requête API, mais à reconsidérer si la révocation immédiate de session s'avère critique (ex. désactivation d'un compte compromis) — dans ce cas, une liste de révocation courte en Redis peut compléter les JWT.

## Conséquences

- Nécessite une gestion explicite de la rotation et de l'expiration des refresh tokens, ainsi qu'un mécanisme de révocation (a minima liste noire en Redis) pour couvrir la désactivation immédiate d'un compte exigée en section 11.6 du PRD.
- Le contrôle des tentatives de connexion (rate limiting) doit être implémenté côté FastAPI (ex. middleware ou dépendance dédiée), indépendamment du choix JWT.
- À valider explicitement avant l'implémentation de l'authentification : ce choix n'a pas été discuté avec l'utilisateur.
