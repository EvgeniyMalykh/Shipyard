class StripeClient:
    """
    Thin wrapper providing:
    - create_checkout_session(team, plan, interval) → Session
    - create_customer_portal_session(team) → Session
    - create_or_get_customer(team) → Customer
    - cancel_subscription(subscription) → None
    - sync_subscription_from_stripe(stripe_sub_id) → Subscription
    """