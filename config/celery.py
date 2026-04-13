import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("shipyard")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# ── Periodic Tasks (Celery Beat) ─────────────────────────────────────────────
app.conf.beat_schedule = {
    # Sync Stripe subscription statuses every hour
    "sync-stripe-subscriptions": {
        "task":     "apps.billing.tasks.sync_stripe_subscriptions",
        "schedule": crontab(minute=0),
    },
    # Clean up expired tokens daily at 3am UTC
    "cleanup-expired-tokens": {
        "task":     "apps.core.tasks.cleanup_expired_tokens",
        "schedule": crontab(hour=3, minute=0),
    },
    # Expire pending invitations daily at 3:30am UTC
    "expire-invitations": {
        "task":     "apps.teams.tasks.expire_pending_invitations",
        "schedule": crontab(hour=3, minute=30),
    },
}

# ── Queue Routing ─────────────────────────────────────────────────────────────
app.conf.task_routes = {
    "apps.notifications.tasks.*": {"queue": "emails"},
    "apps.billing.tasks.*":       {"queue": "billing"},
    "*":                          {"queue": "default"},
}

app.conf.task_serializer        = "json"
app.conf.result_serializer      = "json"
app.conf.accept_content         = ["json"]
app.conf.task_acks_late         = True
app.conf.worker_prefetch_multiplier = 1