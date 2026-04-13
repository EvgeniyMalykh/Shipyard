from django.db import models
from apps.core.models import TimestampedModel
from apps.users.models import User


class EmailLog(TimestampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="email_logs")
    subject = models.CharField(max_length=255)
    recipient = models.EmailField()
    template = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error = models.TextField(blank=True)

    class Meta:
        db_table = "notifications_email_log"

    def __str__(self):
        return f"{self.subject} → {self.recipient}"
