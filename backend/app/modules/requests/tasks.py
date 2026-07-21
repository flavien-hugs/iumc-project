from app.core.celery_app import celery_app
from app.core.email import send_email


@celery_app.task(name="requests.send_acknowledgment")
def send_acknowledgment(email: str, full_name: str, reference: str, service_title: str) -> None:
    """Accusé de réception d'une demande (PRD section 19.2)."""
    body = (
        f"Bonjour {full_name},\n\n"
        f"Nous avons bien reçu votre demande concernant « {service_title} ».\n"
        f"Votre référence : {reference}. Conservez-la pour vos échanges avec IUMC.\n\n"
        "Un conseiller vous recontactera selon votre préférence de contact, "
        "généralement sous 48 heures ouvrées.\n\n"
        "IUMC, Ivoire Univers Multiservices et Commerces\n"
        "Bouaké, quartier Koko"
    )
    send_email(email, f"Votre demande {reference} a bien été reçue", body)
