from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import EmailVerificationToken, PasswordResetToken, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "full_name", "is_active", "is_staff", "is_email_verified", "date_joined"]
    list_filter = ["is_active", "is_staff", "is_email_verified"]
    search_fields = ["email", "full_name"]
    ordering = ["-date_joined"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("full_name", "avatar", "timezone")}),
        ("Stripe", {"fields": ("stripe_customer_id",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "is_email_verified")}),
        ("Dates", {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "full_name", "password1", "password2")}),
    )


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at"]
    search_fields = ["user__email"]


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at"]
    search_fields = ["user__email"]
