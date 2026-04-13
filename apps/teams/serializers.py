from rest_framework import serializers

from .models import Team, TeamInvitation, TeamMembership


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name", "slug", "created_at"]
        read_only_fields = ["id", "slug", "created_at"]


class TeamMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = TeamMembership
        fields = ["id", "user_email", "user_full_name", "role", "created_at"]
        read_only_fields = ["id", "created_at"]


class TeamInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamInvitation
        fields = ["id", "email", "role", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]
