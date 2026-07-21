# ADR-0014 : Architecture backend modulaire par domaine métier

**Date :** 2026-07-17
**Statut :** Accepté

## Contexte

Le backend FastAPI était organisé en couches horizontales (`models/`, `schemas/`, `api/v1/`, `services/`) : chaque fonctionnalité éparpillait son code dans quatre dossiers, et les fichiers de couche (`api/v1/admin.py`, `models/contenu.py`) mélangeaient déjà plusieurs domaines. Les gros modules à venir du panel (gestion des demandes complète, contenus, utilisateurs, rendez-vous, médias — PRD section 11) aggraveraient cette dispersion.

## Décision

Le backend est réorganisé en **modules métier autonomes** sous `app/modules/`, chacun regroupant ses modèles, schémas, routeurs et services :

```
app/
  core/            → socle transverse : config, db (Base + session), sécurité,
                     limitation (anti-abus Redis), redis, celery
  modules/
    auth/          → connexion/déconnexion/rafraîchissement, dépendances d'accès
    utilisateurs/  → Utilisateur, JetonReinitialisation
    contenus/      → Pole, Service, Article, Faq
    implantations/ → Implantation
    demandes/      → Demande, DemandeHistorique, RendezVous, routeurs public et admin
    contact/       → MessageContact, routeur public
    notifications/ → Notification (in-app, ADR-0010)
    journal/       → JournalActivite, service journaliser()
    parametres/    → Parametre
    medias/        → Media
    statistiques/  → tableau de bord (agrège plusieurs domaines)
  models.py        → agrégateur : re-exporte tous les modèles et enums
                     (stabilité des imports `from app.models import X`,
                      et découverte des tables par Alembic)
  api/v1/router.py → assemble les routeurs des modules (versionnement conservé)
```

Chaque module possède ses enums (les statuts de demande vivent dans `demandes/`, les rôles dans `utilisateurs/`, etc.).

## Alternatives envisagées

- **Conserver les couches horizontales** — simple tant que le projet est petit, mais chaque module du panel à venir aurait éclaté son code en 4 endroits ; écarté.
- **Un package Python par module avec son propre versionnement (style micro-services)** — disproportionné : un seul déploiement, une seule base ; écarté.

## Conséquences

- Toute nouvelle fonctionnalité vit dans un module unique (modèles + schémas + routeur + service) ; le socle `core/` ne contient que du transverse sans logique métier.
- `app/models.py` doit être tenu à jour quand un module ajoute un modèle, sinon Alembic ne voit pas la table (l'agrégateur est importé par `migrations/env.py`).
- Les imports croisés entre modules passent par l'agrégateur (`app.models`) pour les modèles, et par le module source pour les services (ex. `app.modules.journal.service.journaliser`) ; un module ne doit pas importer le routeur d'un autre module.
- Restructuration à schéma constant : aucune migration engendrée, vérifié par autogénération à vide.
