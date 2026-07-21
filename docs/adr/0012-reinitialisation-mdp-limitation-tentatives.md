# ADR-0012 : Réinitialisation de mot de passe et limitation des tentatives de connexion

**Date :** 2026-07-17
**Statut :** Proposé

## Contexte

Le PRD (section 11.1) exige explicitement, pour l'authentification du panel : la possibilité de demander une réinitialisation de mot de passe, de modifier son mot de passe, et un « contrôle des tentatives » de connexion. [ADR-0008](./0008-authentification-panel-admin.md) tranche le mécanisme d'authentification (JWT en cookie httpOnly) mais ne couvre ni le flux de réinitialisation, ni le mécanisme concret de limitation des tentatives.

## Décision

**Réinitialisation de mot de passe :** un token à usage unique, à durée de vie limitée (1 heure), haché en base avant stockage, est généré à la demande de l'utilisateur et envoyé par e-mail (tâche asynchrone, [ADR-0005](./0005-taches-asynchrones-celery-redis.md)) sous forme de lien vers une page SvelteKit dédiée de saisie du nouveau mot de passe. Le token est invalidé après utilisation ou expiration.

**Limitation des tentatives de connexion :** un compteur glissant en **Redis**, clé par compte ET par adresse IP, limite les tentatives échouées (ex. 5 tentatives / 15 minutes) avant un verrouillage temporaire du compte. Chaque tentative (réussie ou échouée) et chaque verrouillage sont enregistrés dans le journal d'activité (PRD section 11.8).

## Alternatives envisagées

- **CAPTCHA sur le formulaire de connexion du panel** — écarté : le panel est un accès interne (pas un formulaire public exposé à un trafic massif comme les formulaires de contact/demande, PRD section 10.7 qui eux nécessitent une protection anti-robot). Le verrouillage par compteur suffit pour ce contexte d'usage interne.
- **Blocage uniquement par IP (au niveau Nginx/pare-feu)** — écarté seul : n'empêche pas une énumération de comptes depuis des IP différentes ; retenu en complément possible mais pas comme mécanisme principal. La limitation applicative par compte + IP reste la décision première.
- **Verrouillage définitif après N échecs (nécessitant une intervention manuelle)** — écarté : trop pénalisant pour un utilisateur légitime ayant oublié son mot de passe ; un verrouillage temporaire avec expiration automatique est privilégié.

## Conséquences

- Réutilise Redis déjà introduit par [ADR-0005](./0005-taches-asynchrones-celery-redis.md), sans infrastructure supplémentaire.
- Réutilise l'envoi d'e-mails asynchrone déjà décidé pour le lien de réinitialisation.
- Nécessite une table ou un champ dédié pour stocker le hash et l'expiration des tokens de réinitialisation, et un endpoint FastAPI spécifique pour leur validation.
- Le journal d'activité (section 11.8 du PRD) doit être alimenté par les tentatives de connexion et les verrouillages, pas seulement par les actions de contenu.
