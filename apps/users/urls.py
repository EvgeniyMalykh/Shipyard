urlpatterns = [
    path("register/",              RegisterView.as_view()),
    path("login/",                 LoginView.as_view()),
    path("logout/",                LogoutView.as_view()),
    path("token/refresh/",         TokenRefreshView.as_view()),
    path("verify-email/",          EmailVerifyView.as_view()),
    path("me/",                    UserProfileView.as_view()),
    path("password/change/",       PasswordChangeView.as_view()),
    path("password/reset/",        PasswordResetRequestView.as_view()),
    path("password/reset/confirm/",PasswordResetConfirmView.as_view()),
    path("social/<str:provider>/", SocialAuthView.as_view()),
]