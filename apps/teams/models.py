import uuid
from django.db import models
from apps.core.models import TimestampedModel
from apps.users.models import User


class Team(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    logo = models.ImageField(upload_to="team_logos/", blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="owned_teams")
    members = models.ManyToManyField(User, through="TeamMembership", related_name="teams")
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    max_members = models.PositiveIntegerField(default=3)
    max_projects = models.PositiveIntegerField(default=5)

    class Meta:
        db_table = "teams_team"

    def __str__(self):
        return self.name


class TeamMembership(TimestampedModel):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)

    class Meta:
        db_table = "teams_membership"
        unique_together = [("team", "user")]
        indexes = [models.Index(fields=["team", "role"])]


class TeamInvitation(TimestampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="invitations")
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_invitations")
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=TeamMembership.Role.choices, default=TeamMembership.Role.MEMBER)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "teams_invitation"
        unique_together = [("team", "email")]
