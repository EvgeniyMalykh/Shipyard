import re
from django.core.exceptions import ValidationError


def validate_phone_number(value: str) -> None:
    pattern = re.compile(r"^\+?1?\d{9,15}$")
    if not pattern.match(value):
        raise ValidationError("Enter a valid phone number.")


def validate_no_spaces(value: str) -> None:
    if " " in value:
        raise ValidationError("This field may not contain spaces.")
