from django.contrib import admin
from .models import Team, TeamMembership, TeamInvitation


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "owner", "created_at"]
    search_fields = ["name", "owner__email"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ["team", "user", "role", "created_at"]
    list_filter = ["role"]
    search_fields = ["team__name", "user__email"]


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ["team", "email", "role", "status", "created_at"]
    list_filter = ["status", "role"]
    search_fields = ["team__name", "email"]
