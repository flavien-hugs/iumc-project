import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings


logger = logging.getLogger("iumc.email")


def send_email(to: str, subject: str, body: str) -> None:
    """Envoie un e-mail via SMTP si configuré ; sinon le journalise (dev)."""
    if not settings.smtp_host:
        logger.info("E-mail (non envoyé, SMTP absent) → %s | %s\n%s", to, subject, body)
        return

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.starttls()
        if settings.smtp_user and settings.smtp_password:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)
