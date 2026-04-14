from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """JWT authentication that also checks httpOnly cookie as fallback."""

    def authenticate(self, request):
        header_result = super().authenticate(request)
        if header_result is not None:
            return header_result
        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
