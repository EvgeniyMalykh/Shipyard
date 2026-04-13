import uuid
from django.db import models
from apps.core.models import TimestampedModel
from apps.teams.models import Team


class Plan(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    stripe_product_id = models.CharField(max_length=255, unique=True)
    stripe_price_id_monthly = models.CharField(max_length=255, blank=True)
    stripe_price_id_yearly = models.CharField(max_length=255, blank=True)
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    max_members = models.PositiveIntegerField(default=3)
    max_projects = models.PositiveIntegerField(default=5)
    has_api_access = models.BooleanField(default=False)
    has_priority_support = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "billing_plan"

    def __str__(self):
        return self.name


class Subscription(TimestampedModel):
    class Status(models.TextChoices):
        TRIALING = "trialing", "Trialing"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past Due"
        CANCELLED = "cancelled", "Cancelled"
        UNPAID = "unpaid", "Unpaid"
        INCOMPLETE = "incomplete", "Incomplete"

    class BillingInterval(models.TextChoices):
        MONTHLY = "month", "Monthly"
        YEARLY = "year", "Yearly"

    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=Status.choices)
    billing_interval = models.CharField(max_length=10, choices=BillingInterval.choices, default=BillingInterval.MONTHLY)
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "billing_subscription"
        indexes = [models.Index(fields=["stripe_subscription_id"])]


class Invoice(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        PAID = "paid", "Paid"
        VOID = "void", "Void"
        UNCOLLECTIBLE = "uncollectible", "Uncollectible"

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="invoices")
    stripe_invoice_id = models.CharField(max_length=255, unique=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="usd")
    status = models.CharField(max_length=20, choices=Status.choices)
    invoice_pdf = models.URLField(blank=True)
    hosted_invoice_url = models.URLField(blank=True)
    period_start = models.DateTimeField(null=True)
    period_end = models.DateTimeField(null=True)

    class Meta:
        db_table = "billing_invoice"


class WebhookEvent(TimestampedModel):
    stripe_event_id = models.CharField(max_length=255, unique=True, db_index=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(blank=True)

    class Meta:
        db_table = "billing_webhook_event"
