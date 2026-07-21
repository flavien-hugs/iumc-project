# ADR-0006 : Stockage des médias — local puis S3/MinIO

**Date :** 2026-07-17
**Statut :** Accepté

## Contexte

Le PRD (section 17.5) et le CDC (section 12.1) prévoient un stockage local sécurisé pour le MVP, avec une évolution vers MinIO ou un service compatible S3 en production. La médiathèque doit gérer images, logos, vidéos, documents PDF (CDC section 8.11), et les pièces jointes des demandes clients doivent rester strictement privées (PRD section 14, CDC section 13).

## Décision

Le stockage des fichiers utilisera une **abstraction de stockage unique** (interface commune) implémentée initialement par un **stockage disque local** (volume Docker), avec bascule prévue vers **MinIO (ou S3)** sans changement de code applicatif — seule la configuration/l'implémentation du driver change.

## Alternatives envisagées

- **S3/MinIO dès le MVP** — écarté pour la première version afin de limiter la complexité opérationnelle initiale (pas de service supplémentaire à opérer), conformément à la recommandation des docs. Reste l'option ciblée pour la production dès que le volume de médias ou les besoins de scalabilité l'exigent.
- **Stockage en base (BLOB PostgreSQL)** — écarté : dégrade les performances de la base pour des fichiers volumineux (vidéos, PDF) et complique les sauvegardes.

## Conséquences

- L'abstraction de stockage doit être définie dès le scaffolding backend pour éviter un couplage direct au système de fichiers local dans le code métier.
- Les pièces jointes des demandes clients doivent être servies via des URLs signées ou un contrôle d'accès applicatif (jamais via un chemin statique public), quel que soit le backend de stockage — exigence de confidentialité (PRD section 14).
- La migration vers MinIO/S3 nécessitera un script de transfert des fichiers existants au moment du passage en production à plus grande échelle.
- Le contrôle du **format et de la taille maximale des fichiers** (formats autorisés configurables, taille max configurable — PRD section 10.8, CDC section 8.11) doit être appliqué **au niveau applicatif, avant l'appel à l'abstraction de stockage** (validation du type MIME réel du contenu, pas seulement de l'extension, et de la taille), pour rester valable quel que soit le driver de stockage actif.
