from rest_framework.permissions import BasePermission


class HasActiveSubscription(BasePermission):
    """Allow access only to users with an active subscription."""

    message = "An active subscription is required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.subscriptions.filter(status="active").exists()
