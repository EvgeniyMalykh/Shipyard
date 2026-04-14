import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def delete_unverified_users() -> None:
    """Delete users who never verified their email after 7 days."""
    from datetime import timedelta
    from django.utils import timezone
    from django.contrib.auth import get_user_model

    User = get_user_model()
    cutoff = timezone.now() - timedelta(days=7)
    deleted, _ = User.objects.filter(
        is_email_verified=False,
        date_joined__lt=cutoff,
    ).delete()
    logger.info("delete_unverified_users: deleted %d users", deleted)
