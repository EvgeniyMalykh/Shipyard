import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def expire_pending_invitations() -> None:
    """Mark invitations older than 7 days as expired."""
    from apps.teams.models import TeamInvitation

    cutoff = timezone.now() - timedelta(days=7)
    expired = TeamInvitation.objects.filter(
        status="pending",
        created_at__lt=cutoff,
    ).update(status="expired")
    logger.info("expire_pending_invitations: expired %d invitations", expired)
