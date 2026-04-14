import stripe
from django.conf import settings

stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")


def create_customer(email: str, name: str = "") -> stripe.Customer:
    return stripe.Customer.create(email=email, name=name)


def create_checkout_session(customer_id: str, price_id: str, success_url: str, cancel_url: str) -> stripe.checkout.Session:
    return stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
    )


def cancel_subscription(subscription_id: str) -> stripe.Subscription:
    return stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)


def construct_webhook_event(payload: bytes, sig_header: str) -> stripe.Event:
    return stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
