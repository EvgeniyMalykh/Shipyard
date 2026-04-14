from django.contrib import admin
from .models import Invoice, Plan, Subscription, WebhookEvent


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price_monthly", "price_yearly", "is_active", "is_public")
    list_filter = ("is_active", "is_public")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("team", "plan", "status", "billing_interval", "current_period_end")
    list_filter = ("status", "billing_interval")
    search_fields = ("team__name", "stripe_subscription_id")
    readonly_fields = ("stripe_subscription_id",)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("team", "stripe_invoice_id", "status", "amount_due", "currency")
    list_filter = ("status", "currency")
    search_fields = ("team__name", "stripe_invoice_id")
    readonly_fields = ("stripe_invoice_id",)


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "stripe_event_id", "processed_at")
    list_filter = ("event_type",)
    search_fields = ("event_type", "stripe_event_id")
    readonly_fields = ("stripe_event_id", "payload")
