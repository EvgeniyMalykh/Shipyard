from celery import shared_task


@shared_task
def health_check() -> str:
    """Periodic health check task."""
    return "ok"
