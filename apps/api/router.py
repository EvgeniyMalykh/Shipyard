router = DefaultRouter()

# Register all app ViewSets here — single source of truth for API routing
router.register(r"teams",                    TeamViewSet,                 basename="team")
router.register(r"teams/(?P<team_id>[^/.]+)/members",
                TeamMembershipViewSet,        basename="team-member")
router.register(r"teams/(?P<team_id>[^/.]+)/invitations",
                TeamInvitationViewSet,        basename="team-invitation")