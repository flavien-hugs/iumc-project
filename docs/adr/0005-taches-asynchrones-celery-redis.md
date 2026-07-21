# ADR-0005 : Traitement asynchrone — Celery + Redis

**Date :** 2026-07-17
**Statut :** Proposé

## Contexte

Le PRD (section 17.4) et le CDC mentionnent Celery pour l'envoi d'e-mails, le traitement de notifications, la génération d'exports et les tâches planifiées (programmation d'articles, notifications de rendez-vous — PRD section 19). Celery nécessite un broker de messages ; ce choix n'est pas précisé dans les documents source.

## Décision

Les tâches asynchrones seront gérées par **Celery**, avec **Redis** comme broker de messages et backend de résultats.

## Alternatives envisagées

- **RabbitMQ** — broker plus robuste pour des charges élevées et des garanties de livraison strictes, mais plus complexe à opérer. Écarté pour le MVP : le volume de tâches attendu (e-mails transactionnels, quelques exports, programmation d'articles) ne justifie pas cette complexité opérationnelle supplémentaire.
- **Pas de file de tâches (traitement synchrone)** — écarté : l'envoi d'e-mails et de notifications en synchrone dans la requête HTTP dégraderait le temps de réponse des formulaires publics, contraire à l'exigence de performance (CDC section 14).

## Conséquences

- Redis peut être réutilisé comme cache applicatif (mise en cache mentionnée en PRD section 13.1 et CDC section 14), réduisant le nombre de services à opérer.
- Si le volume de tâches critiques augmente fortement (post-MVP), une migration vers RabbitMQ reste possible sans changer la couche applicative Celery.
- À valider avec l'équipe technique avant scaffolding : ce choix n'a pas été explicitement discuté, contrairement aux ADR 0002 à 0004.
