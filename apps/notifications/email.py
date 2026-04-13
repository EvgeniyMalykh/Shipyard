class BaseEmail:
    subject: str
    template_name: str
    from_email: str = settings.DEFAULT_FROM_EMAIL

    def __init__(self, to: str, context: dict):
        self.to      = to
        self.context = context

    def get_context(self) -> dict:
        return {"site_name": "Shipyard", "support_email": settings.SUPPORT_EMAIL,
                **self.context}

    def render(self) -> tuple[str, str]:
        """Returns (html_body, text_body)."""

    def send(self) -> None:
        """Renders and sends via Django's email backend (SES/SMTP/console)."""


class WelcomeEmail(BaseEmail):
    subject       = "Welcome to {{ site_name }}"
    template_name = "notifications/welcome.html"
    # context: user


class VerificationEmail(BaseEmail):
    subject       = "Verify your email address"
    template_name = "notifications/verify_email.html"
    # context: user, verification_url


class PasswordResetEmail(BaseEmail):
    subject       = "Reset your password"
    template_name = "notifications/password_reset.html"
    # context: user, reset_url, expires_in


class InvitationEmail(BaseEmail):
    subject       = "You've been invited to {{ team_name }}"
    template_name = "notifications/invitation.html"
    # context: team, invited_by, invitation_url, role


class BillingAlertEmail(BaseEmail):
    subject       = "Action required: payment issue on {{ team_name }}"
    template_name = "notifications/billing_alert.html"
    # context: team, invoice


class SubscriptionCancelledEmail(BaseEmail):
    subject       = "Your {{ site_name }} subscription has been cancelled"
    template_name = "notifications/subscription_cancelled.html"
    # context: team, plan, end_date