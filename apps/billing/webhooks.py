import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Subscription, WebhookEvent
from .stripe_client import construct_webhook_event

logger = logging.getLogger(__name__)

HANDLED_EVENTS = {
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.payment_succeeded",
    "invoice.payment_failed",
}


@csrf_exempt
@require_POST
def stripe_webhook(request):
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = construct_webhook_event(request.body, sig_header)
    except Exception as e:
        logger.warning("Webhook signature verification failed: %s", e)
        return HttpResponse(status=400)

    WebhookEvent.objects.get_or_create(
        stripe_event_id=event["id"],
        defaults={"event_type": event["type"], "payload": event},
    )

    if event["type"] == "customer.subscription.updated":
        _handle_subscription_updated(event["data"]["object"])
    elif event["type"] == "customer.subscription.deleted":
        _handle_subscription_deleted(event["data"]["object"])

    return HttpResponse(status=200)


def _handle_subscription_updated(subscription_data: dict) -> None:
    Subscription.objects.filter(
        stripe_subscription_id=subscription_data["id"]
    ).update(status=subscription_data["status"])


def _handle_subscription_deleted(subscription_data: dict) -> None:
    Subscription.objects.filter(
        stripe_subscription_id=subscription_data["id"]
    ).update(status="canceled")
