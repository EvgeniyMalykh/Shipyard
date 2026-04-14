import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    if created:
        logger.info("New user registered: %s", instance.email)
        from apps.notifications.tasks import send_welcome_email
        send_welcome_email.delay(str(instance.id))
