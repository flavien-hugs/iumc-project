"""Nettoyage du HTML produit par l'éditeur riche du panel (Tiptap).

Le contenu est rédigé par des utilisateurs authentifiés, mais reste affiché
tel quel à tous les visiteurs du site public : un compte compromis ou un
appel direct à l'API (hors de l'éditeur) pourrait sinon injecter du script
côté client (XSS stocké). On restreint donc strictement les balises et
attributs à ce que la barre d'outils peut réellement produire.
"""

import bleach

ALLOWED_TAGS = ["p", "h2", "h3", "strong", "em", "ul", "ol", "li", "a", "br"]
ALLOWED_ATTRIBUTES = {"a": ["href", "rel", "target"]}
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_html(value: str | None) -> str | None:
    if value is None:
        return None
    return bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
