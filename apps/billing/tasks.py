import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def sync_stripe_subscriptions(self) -> None:
    """Sync subscription statuses from Stripe."""
    try:
        logger.info("sync_stripe_subscriptions: started")
        # TODO: implement Stripe sync
    except Exception as exc:
        logger.error("sync_stripe_subscriptions failed: %s", exc)
        raise self.retry(exc=exc)
