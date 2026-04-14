from django.urls import path
from .views import InviteMemberView, TeamDetailView, TeamListCreateView, TeamMembersView

urlpatterns = [
    path("", TeamListCreateView.as_view(), name="team_list"),
    path("<uuid:pk>/", TeamDetailView.as_view(), name="team_detail"),
    path("<uuid:pk>/members/", TeamMembersView.as_view(), name="team_members"),
    path("<uuid:pk>/invite/", InviteMemberView.as_view(), name="team_invite"),
]
