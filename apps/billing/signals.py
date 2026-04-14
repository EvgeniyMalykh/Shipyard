import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Subscription

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Subscription)
def on_subscription_change(sender, instance, created, **kwargs):
    if created:
        logger.info("New subscription created: user=%s plan=%s", instance.user_id, instance.plan_id)
    elif instance.status == "canceled":
        logger.info("Subscription canceled: user=%s", instance.user_id)
