import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TeamInvitation

logger = logging.getLogger(__name__)


@receiver(post_save, sender=TeamInvitation)
def on_invitation_created(sender, instance, created, **kwargs):
    if created:
        logger.info("Team invitation sent: %s -> %s", instance.team.name, instance.email)
