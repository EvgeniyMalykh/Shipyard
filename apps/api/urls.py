from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.billing.views import InvoiceListView, PlanListView, SubscriptionView
from apps.teams.views import InviteMemberView, TeamDetailView, TeamListCreateView, TeamMembersView
from apps.users.views import ChangePasswordView, MeView, RegisterView

urlpatterns = [
    # Auth
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Users
    path("users/me/", MeView.as_view(), name="me"),
    path("users/me/password/", ChangePasswordView.as_view(), name="change_password"),

    # Teams
    path("teams/", TeamListCreateView.as_view(), name="team_list"),
    path("teams/<uuid:pk>/", TeamDetailView.as_view(), name="team_detail"),
    path("teams/<uuid:pk>/members/", TeamMembersView.as_view(), name="team_members"),
    path("teams/<uuid:pk>/invite/", InviteMemberView.as_view(), name="team_invite"),

    # Billing
    path("billing/plans/", PlanListView.as_view(), name="plan_list"),
    path("billing/subscription/", SubscriptionView.as_view(), name="subscription"),
    path("billing/invoices/", InvoiceListView.as_view(), name="invoice_list"),
]
