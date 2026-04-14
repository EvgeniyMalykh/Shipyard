import uuid
from django.utils.text import slugify


def generate_unique_slug(model_class, value: str, slug_field: str = "slug") -> str:
    slug = slugify(value)
    unique_slug = slug
    num = 1
    while model_class.objects.filter(**{slug_field: unique_slug}).exists():
        unique_slug = f"{slug}-{num}"
        num += 1
    return unique_slug


def generate_uuid() -> str:
    return str(uuid.uuid4())
