class IsEmailVerified(BasePermission):
    """Allow access only to users who have verified their email address."""
    message = "Email address not verified."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.is_email_verified)


class IsSelf(BasePermission):
    """Object-level permission: allow only if the object IS the requesting user."""
    def has_object_permission(self, request, view, obj):
        return obj == request.user