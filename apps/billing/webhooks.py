WEBHOOK_HANDLERS: dict[str, Callable] = {
    "checkout.session.completed":          handle_checkout_completed,
    "customer.subscription.created":       handle_subscription_created,
    "customer.subscription.updated":       handle_subscription_updated,
    "customer.subscription.deleted":       handle_subscription_deleted,
    "invoice.payment_succeeded":           handle_invoice_paid,
    "invoice.payment_failed":              handle_invoice_payment_failed,
    "customer.subscription.trial_will_end": handle_trial_ending,
}

def process_webhook(event: stripe.Event) -> None:
    """
    Entry point from WebhookView.
    1. Check WebhookEvent for idempotency (skip if already processed).
    2. Dispatch to the appropriate handler.
    3. Mark event as processed or log the error.
    """