import logging
logger = logging.getLogger(__name__)


def get_user_by_email(email: str):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None
