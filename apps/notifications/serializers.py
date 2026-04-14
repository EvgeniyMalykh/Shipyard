from rest_framework import serializers
from .models import EmailLog


class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = ["id", "to_email", "subject", "status", "created_at"]
        read_only_fields = ["id", "created_at"]
