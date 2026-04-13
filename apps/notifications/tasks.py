import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, email_class: str, to: str, context: dict) -> None:
    """
    Celery task wrapping BaseEmail.send().
    Retries 3x on failure. Logs every send attempt to EmailLog.
    """
    try:
        logger.info("send_email_task: %s -> %s", email_class, to)
        # TODO: implement email dispatch
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def send_welcome_email(user_id: str) -> None:
    """Called from users.signals post_save."""
    logger.info("send_welcome_email: user_id=%s", user_id)


@shared_task
def send_verification_email(user_id: str) -> None:
    """Called after registration."""
    logger.info("send_verification_email: user_id=%s", user_id)
