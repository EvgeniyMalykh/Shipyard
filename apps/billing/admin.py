from django.contrib import admin

from .models import Invoice, Plan, Subscription, WebhookEvent


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price_monthly", "price_yearly", "is_active"]
    list_filter = ["is_active"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "status", "current_period_end", "cancel_at_period_end"]
    list_filter = ["status"]
    search_fields = ["user__email", "stripe_subscription_id"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "currency", "status", "created_at"]
    list_filter = ["status", "currency"]
    search_fields = ["user__email", "stripe_invoice_id"]


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ["event_type", "processed", "created_at"]
    list_filter = ["processed", "event_type"]
