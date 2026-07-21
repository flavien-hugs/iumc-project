# ADR-0015 : Convention de nommage — code en anglais, contenu en français

**Date :** 2026-07-17
**Statut :** Accepté

## Contexte

Le code (modules, classes, fonctions, colonnes, schémas d'API) avait été écrit avec des identifiants français collant au vocabulaire du PRD. Cela crée des frictions : mélange avec les mots-clés anglais des frameworks, outillage et générateurs pensés pour l'anglais, onboarding de développeurs non francophones.

## Décision

**Tout identifiant technique est en anglais** : noms de modules, classes, fonctions, variables, tables, colonnes, enums, routes d'API et clés JSON. Correspondances principales du domaine :

| Domaine (PRD) | Code |
|---|---|
| pôle | division |
| demande | service request |
| implantation | location |
| rendez-vous | appointment |
| journal d'activité | audit log |
| utilisateur | user |
| paramètre | setting |

Restent **en français** : le contenu destiné aux utilisateurs (libellés, messages d'erreur API affichables, textes du site), les URLs publiques du site vitrine (`/fr/demande`, `/fr/implantations` — enjeu SEO local), la référence métier `IUMC-DEM-AAAA-NNNNN` (format imposé par le PRD section 10.8), et la documentation projet (docs/, ADR).

## Alternatives envisagées

- **Conserver le français dans le code** — cohérent avec le PRD mais contraire aux usages de l'écosystème ; écarté à la demande explicite du projet.
- **Anglais partout, y compris URLs publiques** — écarté : les URLs du site public ciblent des recherches locales francophones (CDC section 10).

## Conséquences

- Le schéma de base de données passe en anglais : la migration initiale est régénérée et la base de développement réinitialisée (données de test uniquement, aucune donnée réelle à ce stade).
- Le contrat d'API change (routes `/auth/login`, `/service-requests`, clés JSON anglaises) : les deux apps frontend sont mises à jour dans le même mouvement.
- Toute contribution future suit cette convention ; un identifiant français dans le code est à considérer comme une dette à corriger.
