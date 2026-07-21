from app.core.celery_app import celery_app
from app.core.email import send_email


@celery_app.task(name="users.send_password_reset")
def send_password_reset(email: str, reset_link: str) -> None:
    """Lien de réinitialisation de mot de passe (ADR-0012), valable 1 heure."""
    body = (
        "Bonjour,\n\n"
        "Une réinitialisation du mot de passe de votre compte du panel IUMC a été demandée.\n"
        f"Pour définir un nouveau mot de passe, ouvrez ce lien (valable 1 heure) :\n\n"
        f"{reset_link}\n\n"
        "Si vous n'êtes pas à l'origine de cette demande, ignorez ce message.\n\n"
        "IUMC, Ivoire Univers Multiservices et Commerces"
    )
    send_email(email, "Réinitialisation de votre mot de passe IUMC", body)
