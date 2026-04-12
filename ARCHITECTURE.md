# Shipyard — Django SaaS Boilerplate: Complete Architecture

> **Version:** 1.0.0  
> **Stack:** Python 3.12 / Django 5.x / PostgreSQL 16 / Redis / Celery / Docker / Stripe

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Complete File Tree](#2-complete-file-tree)
3. [Django Apps — Detailed Breakdown](#3-django-apps--detailed-breakdown)
   - 3.1 [users](#31-users)
   - 3.2 [teams](#32-teams)
   - 3.3 [billing](#33-billing)
   - 3.4 [api](#34-api)
   - 3.5 [core](#35-core)
   - 3.6 [notifications](#36-notifications)
4. [Infrastructure & Configuration Files](#4-infrastructure--configuration-files)
   - 4.1 [Docker & Compose](#41-docker--compose)
   - 4.2 [Nginx](#42-nginx)
   - 4.3 [Celery](#43-celery)
   - 4.4 [GitHub Actions CI/CD](#44-github-actions-cicd)
5. [Environment Variables](#5-environment-variables)
6. [API Design](#6-api-design)
7. [Data Models — Entity Relationship Overview](#7-data-models--entity-relationship-overview)
8. [Authentication Flow](#8-authentication-flow)
9. [Stripe Integration Flow](#9-stripe-integration-flow)
10. [Celery Task Architecture](#10-celery-task-architecture)
11. [README Template](#11-readme-template)

---

## 1. Project Overview

Shipyard is a production-ready Django SaaS boilerplate. Developers purchase it once and use it as the foundation for any multi-tenant SaaS product. It ships with authentication, multi-tenancy, billing, background tasks, file storage, CI/CD, and a full DRF API — all wired together and ready to deploy.

### Design Principles

- **API-first** — Every feature is exposed through versioned DRF endpoints. The Django admin is for operators, not end users.
- **Multi-tenant by default** — Every resource belongs to a Team. User → TeamMembership → Team is the ownership chain throughout the entire codebase.
- **12-factor app** — All configuration via environment variables. Stateless application servers. Logs to stdout.
- **No magic** — Explicit over implicit. No monkeypatching. Settings split by environment. Each app has a single clear responsibility.

---

## 2. Complete File Tree

```
shipyard/
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                      # Lint + test on every push/PR
│   │   ├── build.yml                   # Build & push Docker image on main
│   │   └── deploy.yml                  # Deploy to production on release tag
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md
│
├── apps/
│   ├── users/                          # Custom user model, auth, JWT, social auth
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── managers.py                 # CustomUserManager (email-based)
│   │   ├── models.py                   # User, EmailVerificationToken, PasswordResetToken
│   │   ├── serializers.py              # Register, Login, Profile, PasswordChange
│   │   ├── views.py                    # RegisterView, LoginView, LogoutView, ProfileView, etc.
│   │   ├── urls.py
│   │   ├── permissions.py              # IsEmailVerified, IsSelf
│   │   ├── signals.py                  # post_save: send welcome email
│   │   ├── tasks.py                    # send_welcome_email, send_verification_email
│   │   ├── adapters.py                 # django-allauth SocialAccountAdapter override
│   │   ├── pipeline.py                 # Social auth pipeline steps
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       ├── test_serializers.py
│   │       └── factories.py            # factory_boy User factory
│   │
│   ├── teams/                          # Multi-tenancy: Team, membership, roles, invitations
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                   # Team, TeamMembership, TeamInvitation
│   │   ├── serializers.py              # Team CRUD, Membership, Invitation
│   │   ├── views.py                    # TeamViewSet, MembershipViewSet, InvitationViewSet
│   │   ├── urls.py
│   │   ├── permissions.py              # IsTeamOwner, IsTeamAdmin, IsTeamMember
│   │   ├── signals.py                  # post_save: provision Stripe customer on team create
│   │   ├── tasks.py                    # send_invitation_email
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       └── factories.py
│   │
│   ├── billing/                        # Stripe: plans, subscriptions, webhooks, portal
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                   # Plan, Subscription, Invoice, WebhookEvent
│   │   ├── serializers.py              # Plan, Subscription, CheckoutSession, Portal
│   │   ├── views.py                    # PlanListView, CheckoutView, WebhookView, PortalView
│   │   ├── urls.py
│   │   ├── permissions.py              # HasActiveSubscription, IsWithinPlanLimits
│   │   ├── stripe_client.py            # Thin wrapper around stripe-python SDK
│   │   ├── webhooks.py                 # Webhook event router + handler functions
│   │   ├── signals.py                  # subscription change → notify team owner
│   │   ├── tasks.py                    # sync_stripe_subscriptions, send_billing_alerts
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       ├── test_webhooks.py
│   │       └── factories.py
│   │
│   ├── api/                            # DRF router, versioning, throttling, schema
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── router.py                   # DefaultRouter with all app ViewSets registered
│   │   ├── urls.py                     # /api/v1/ prefix, schema endpoint
│   │   ├── versioning.py               # NamespaceVersioning config
│   │   ├── throttling.py               # AnonRateThrottle, UserRateThrottle, BurstThrottle
│   │   ├── pagination.py               # CursorPagination, PageNumberPagination
│   │   ├── filters.py                  # DRF + django-filter FilterSets
│   │   ├── exceptions.py               # Custom exception handler → uniform JSON errors
│   │   ├── renderers.py                # JSONRenderer with envelope {"data": ..., "meta": ...}
│   │   ├── authentication.py           # JWTAuthentication + SessionAuthentication combo
│   │   ├── schema.py                   # drf-spectacular AutoSchema overrides
│   │   └── tests/
│   │       ├── __init__.py
│   │       └── test_router.py
│   │
│   ├── core/                           # Shared utilities, health check, Sentry, storage
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                   # TimestampedModel, UUIDModel (abstract base models)
│   │   ├── views.py                    # HealthCheckView, ReadinessView
│   │   ├── urls.py                     # /health/, /ready/
│   │   ├── storage.py                  # S3Boto3Storage subclasses (public, private)
│   │   ├── middleware.py               # RequestIDMiddleware, TimezoneMiddleware
│   │   ├── validators.py               # Shared DRF + model validators
│   │   ├── utils.py                    # generate_token(), paginate_queryset(), etc.
│   │   ├── exceptions.py               # ShipyardAPIError base, domain-specific subclasses
│   │   ├── tasks.py                    # cleanup_expired_tokens (periodic), prune_old_logs
│   │   └── tests/
│   │       ├── __init__.py
│   │       └── test_views.py
│   │
│   └── notifications/                  # Transactional email templates + delivery
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py                   # EmailLog (audit trail of every sent email)
│       ├── serializers.py              # (internal — not exposed via API)
│       ├── email.py                    # BaseEmail, WelcomeEmail, VerificationEmail, etc.
│       ├── tasks.py                    # send_email (Celery task wrapping email.py)
│       ├── templates/
│       │   └── notifications/
│       │       ├── base.html           # Base email HTML layout
│       │       ├── welcome.html
│       │       ├── verify_email.html
│       │       ├── password_reset.html
│       │       ├── invitation.html
│       │       ├── billing_alert.html
│       │       └── subscription_cancelled.html
│       └── tests/
│           ├── __init__.py
│           └── test_email.py
│
├── config/                             # Django settings, WSGI, ASGI, Celery entry points
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                     # All shared settings
│   │   ├── development.py              # DEBUG=True, local DB, console email backend
│   │   ├── production.py               # Gunicorn, S3, Redis, Sentry, strict security
│   │   └── testing.py                  # Fast password hasher, in-memory SQLite or test PG
│   ├── urls.py                         # Root URL conf
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py                       # Celery app instance + autodiscover
│
├── docker/
│   ├── dev/
│   │   ├── Dockerfile                  # Development image (includes dev dependencies)
│   │   └── entrypoint.sh               # migrate + collectstatic + runserver
│   ├── prod/
│   │   ├── Dockerfile                  # Multi-stage production image
│   │   └── entrypoint.sh               # migrate + collectstatic + gunicorn
│   ├── nginx/
│   │   ├── nginx.dev.conf              # Dev: proxy to Django, no SSL
│   │   ├── nginx.prod.conf             # Prod: SSL termination, static/media, rate limiting
│   │   └── ssl/                        # Certbot-managed (gitignored)
│   └── postgres/
│       └── init.sql                    # Create DB extensions (uuid-ossp, pg_trgm)
│
├── docs/
│   ├── architecture.md                 # (this file, symlinked)
│   ├── api.md                          # API endpoint reference
│   ├── deployment.md                   # Step-by-step production deployment guide
│   ├── environment-variables.md        # Full env var reference
│   ├── stripe-setup.md                 # Stripe account, webhook, product setup
│   ├── social-auth-setup.md            # Google + GitHub OAuth app configuration
│   └── customization-guide.md          # How to fork and extend Shipyard
│
├── locale/                             # i18n message files
│   └── en/
│       └── LC_MESSAGES/
│           ├── django.po
│           └── django.mo
│
├── requirements/
│   ├── base.txt                        # Shared dependencies
│   ├── development.txt                 # Dev + test only
│   └── production.txt                 # Prod-only (gunicorn, sentry-sdk, etc.)
│
├── scripts/
│   ├── bootstrap.sh                    # First-time local dev setup
│   ├── seed.sh                         # Create superuser + sample data
│   └── release.sh                      # Tag + push release
│
├── static/                             # Collected static files (gitignored in prod)
│   └── .gitkeep
│
├── media/                              # Local media uploads (dev only; gitignored)
│   └── .gitkeep
│
├── tests/                              # Top-level integration + e2e tests
│   ├── __init__.py
│   ├── conftest.py                     # pytest fixtures: client, user, team, subscription
│   ├── integration/
│   │   ├── test_auth_flow.py           # Register → verify → login → refresh
│   │   ├── test_team_flow.py           # Create team → invite → accept
│   │   └── test_billing_flow.py        # Checkout → webhook → feature gate
│   └── fixtures/
│       ├── stripe_webhook_events/
│       │   ├── checkout.session.completed.json
│       │   ├── customer.subscription.updated.json
│       │   └── invoice.payment_failed.json
│       └── users.json
│
├── .env.example                        # Template with all required variables
├── .gitignore
├── .dockerignore
├── .editorconfig
├── .pre-commit-config.yaml             # ruff, black, isort, mypy
├── docker-compose.yml                  # Development stack
├── docker-compose.prod.yml             # Production stack
├── manage.py
├── pyproject.toml                      # ruff, black, mypy, pytest, coverage config
├── Makefile                            # Shorthand targets: make dev, test, migrate, etc.
└── README.md
```

---

## 3. Django Apps — Detailed Breakdown

---

### 3.1 `users`

**Purpose:** Custom User model with email-based authentication, JWT token management, email verification, social auth integration.

#### `models.py`

```python
class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model. Email is the primary identifier — no username field.
    """
    id            = UUIDField(primary_key=True, default=uuid4, editable=False)
    email         = EmailField(unique=True)
    full_name     = CharField(max_length=255, blank=True)
    avatar        = ImageField(upload_to="avatars/", blank=True, null=True)
    is_active     = BooleanField(default=True)
    is_staff      = BooleanField(default=False)
    is_email_verified = BooleanField(default=False)
    date_joined   = DateTimeField(auto_now_add=True)
    last_login    = DateTimeField(null=True, blank=True)
    timezone      = CharField(max_length=50, default="UTC")
    # Stripe
    stripe_customer_id = CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()

    class Meta:
        db_table = "users_user"
        indexes  = [Index(fields=["email"]), Index(fields=["stripe_customer_id"])]


class EmailVerificationToken(TimestampedModel):
    user       = ForeignKey(User, on_delete=CASCADE, related_name="verification_tokens")
    token      = CharField(max_length=64, unique=True, db_index=True)
    expires_at = DateTimeField()
    used_at    = DateTimeField(null=True, blank=True)


class PasswordResetToken(TimestampedModel):
    user       = ForeignKey(User, on_delete=CASCADE, related_name="password_reset_tokens")
    token      = CharField(max_length=64, unique=True, db_index=True)
    expires_at = DateTimeField()
    used_at    = DateTimeField(null=True, blank=True)
```

#### `serializers.py`

| Serializer | Fields | Purpose |
|---|---|---|
| `RegisterSerializer` | email, full_name, password, password_confirm | New user registration |
| `LoginSerializer` | email, password | Credential validation → returns JWT pair |
| `TokenRefreshSerializer` | refresh | Wraps SimpleJWT |
| `UserProfileSerializer` | id, email, full_name, avatar, timezone, is_email_verified | Read/update own profile |
| `PasswordChangeSerializer` | old_password, new_password, new_password_confirm | Authenticated password change |
| `PasswordResetRequestSerializer` | email | Trigger reset email |
| `PasswordResetConfirmSerializer` | token, new_password, new_password_confirm | Consume reset token |
| `EmailVerificationSerializer` | token | Consume verification token |

#### `views.py`

| View | Method | Endpoint | Auth Required |
|---|---|---|---|
| `RegisterView` | POST | `/api/v1/auth/register/` | No |
| `LoginView` | POST | `/api/v1/auth/login/` | No |
| `LogoutView` | POST | `/api/v1/auth/logout/` | Yes |
| `TokenRefreshView` | POST | `/api/v1/auth/token/refresh/` | No |
| `EmailVerifyView` | POST | `/api/v1/auth/verify-email/` | No |
| `PasswordResetRequestView` | POST | `/api/v1/auth/password/reset/` | No |
| `PasswordResetConfirmView` | POST | `/api/v1/auth/password/reset/confirm/` | No |
| `UserProfileView` | GET, PATCH | `/api/v1/auth/me/` | Yes |
| `PasswordChangeView` | POST | `/api/v1/auth/password/change/` | Yes |
| `SocialAuthView` | POST | `/api/v1/auth/social/{provider}/` | No |

#### `urls.py`

```python
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
```

#### `permissions.py`

```python
class IsEmailVerified(BasePermission):
    """Allow access only to users who have verified their email address."""
    message = "Email address not verified."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.is_email_verified)


class IsSelf(BasePermission):
    """Object-level permission: allow only if the object IS the requesting user."""
    def has_object_permission(self, request, view, obj):
        return obj == request.user
```

---

### 3.2 `teams`

**Purpose:** Multi-tenancy layer. Every tenant is a Team. Users belong to teams through TeamMembership with a role. Invitations allow asynchronous onboarding.

#### `models.py`

```python
class Team(TimestampedModel):
    """
    The top-level tenant. All billable, feature-gated resources hang off a Team.
    """
    id           = UUIDField(primary_key=True, default=uuid4, editable=False)
    name         = CharField(max_length=255)
    slug         = SlugField(unique=True, max_length=255)
    logo         = ImageField(upload_to="team_logos/", blank=True, null=True)
    owner        = ForeignKey(User, on_delete=PROTECT, related_name="owned_teams")
    members      = ManyToManyField(User, through="TeamMembership", related_name="teams")
    # Stripe
    stripe_customer_id = CharField(max_length=255, blank=True, null=True, unique=True)
    # Limits (populated from Plan on subscription activation)
    max_members  = PositiveIntegerField(default=3)
    max_projects = PositiveIntegerField(default=5)   # example resource limit

    class Meta:
        db_table = "teams_team"


class TeamMembership(TimestampedModel):
    class Role(TextChoices):
        OWNER  = "owner",  "Owner"
        ADMIN  = "admin",  "Admin"
        MEMBER = "member", "Member"

    team   = ForeignKey(Team, on_delete=CASCADE, related_name="memberships")
    user   = ForeignKey(User, on_delete=CASCADE, related_name="memberships")
    role   = CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)

    class Meta:
        db_table     = "teams_membership"
        unique_together = [("team", "user")]
        indexes      = [Index(fields=["team", "role"])]


class TeamInvitation(TimestampedModel):
    class Status(TextChoices):
        PENDING  = "pending",  "Pending"
        ACCEPTED = "accepted", "Accepted"
        EXPIRED  = "expired",  "Expired"
        REVOKED  = "revoked",  "Revoked"

    team       = ForeignKey(Team, on_delete=CASCADE, related_name="invitations")
    invited_by = ForeignKey(User, on_delete=CASCADE, related_name="sent_invitations")
    email      = EmailField()
    role       = CharField(max_length=20, choices=TeamMembership.Role.choices,
                           default=TeamMembership.Role.MEMBER)
    token      = CharField(max_length=64, unique=True, db_index=True)
    status     = CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    expires_at = DateTimeField()

    class Meta:
        db_table        = "teams_invitation"
        unique_together = [("team", "email")]
```

#### `serializers.py`

| Serializer | Purpose |
|---|---|
| `TeamSerializer` | Full team detail (name, slug, logo, member count, plan) |
| `TeamCreateSerializer` | name, slug — auto-assigns requesting user as owner |
| `TeamUpdateSerializer` | name, logo — owner/admin only |
| `TeamMembershipSerializer` | member id, email, full_name, role, joined_at |
| `RoleUpdateSerializer` | role — admin can change member roles |
| `TeamInvitationCreateSerializer` | email, role |
| `TeamInvitationSerializer` | Full invitation detail |
| `AcceptInvitationSerializer` | token |

#### `views.py` (ViewSets)

| ViewSet / View | Actions | Endpoint Pattern |
|---|---|---|
| `TeamViewSet` | list, create, retrieve, update, destroy | `/api/v1/teams/` |
| `TeamMembershipViewSet` | list, retrieve, update (role), destroy | `/api/v1/teams/{team_id}/members/` |
| `TeamInvitationViewSet` | list, create, destroy (revoke) | `/api/v1/teams/{team_id}/invitations/` |
| `AcceptInvitationView` | POST | `/api/v1/invitations/accept/` |

#### `permissions.py`

```python
class IsTeamMember(BasePermission):
    """Request user must be a member of the team in the URL kwargs."""

class IsTeamAdmin(BasePermission):
    """Request user must have role=admin or role=owner on the team."""

class IsTeamOwner(BasePermission):
    """Request user must have role=owner on the team."""
    # Used for: team deletion, owner transfer, billing management

class IsTeamOwnerOrAdmin(BasePermission):
    """Either owner or admin; used for most write operations."""
```

---

### 3.3 `billing`

**Purpose:** Stripe integration — plan catalog, subscription lifecycle, checkout sessions, customer portal, webhook event processing, and per-tenant plan limits.

#### `models.py`

```python
class Plan(TimestampedModel):
    """Mirrors a Stripe Product + its Prices. Editable via Django Admin."""
    id              = UUIDField(primary_key=True, default=uuid4, editable=False)
    name            = CharField(max_length=100)                # "Starter", "Pro", "Enterprise"
    slug            = SlugField(unique=True)
    stripe_product_id  = CharField(max_length=255, unique=True)
    stripe_price_id_monthly   = CharField(max_length=255, blank=True)
    stripe_price_id_yearly    = CharField(max_length=255, blank=True)
    price_monthly   = DecimalField(max_digits=8, decimal_places=2)
    price_yearly    = DecimalField(max_digits=8, decimal_places=2)
    is_active       = BooleanField(default=True)
    is_public       = BooleanField(default=True)
    # Feature limits (denormalized for fast access)
    max_members     = PositiveIntegerField(default=3)
    max_projects    = PositiveIntegerField(default=5)
    has_api_access  = BooleanField(default=False)
    has_priority_support = BooleanField(default=False)
    metadata        = JSONField(default=dict, blank=True)      # arbitrary feature flags

    class Meta:
        db_table = "billing_plan"


class Subscription(TimestampedModel):
    class Status(TextChoices):
        TRIALING   = "trialing",   "Trialing"
        ACTIVE     = "active",     "Active"
        PAST_DUE   = "past_due",   "Past Due"
        CANCELLED  = "cancelled",  "Cancelled"
        UNPAID     = "unpaid",     "Unpaid"
        INCOMPLETE = "incomplete", "Incomplete"

    class BillingInterval(TextChoices):
        MONTHLY = "month", "Monthly"
        YEARLY  = "year",  "Yearly"

    team                  = OneToOneField(Team, on_delete=CASCADE, related_name="subscription")
    plan                  = ForeignKey(Plan, on_delete=PROTECT, related_name="subscriptions")
    status                = CharField(max_length=20, choices=Status.choices)
    billing_interval      = CharField(max_length=10, choices=BillingInterval.choices,
                                      default=BillingInterval.MONTHLY)
    stripe_subscription_id = CharField(max_length=255, unique=True)
    current_period_start  = DateTimeField()
    current_period_end    = DateTimeField()
    cancel_at_period_end  = BooleanField(default=False)
    trial_start           = DateTimeField(null=True, blank=True)
    trial_end             = DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "billing_subscription"
        indexes  = [Index(fields=["stripe_subscription_id"])]


class Invoice(TimestampedModel):
    class Status(TextChoices):
        DRAFT   = "draft",   "Draft"
        OPEN    = "open",    "Open"
        PAID    = "paid",    "Paid"
        VOID    = "void",    "Void"
        UNCOLLECTIBLE = "uncollectible", "Uncollectible"

    team             = ForeignKey(Team, on_delete=CASCADE, related_name="invoices")
    stripe_invoice_id = CharField(max_length=255, unique=True)
    amount_due       = DecimalField(max_digits=10, decimal_places=2)
    amount_paid      = DecimalField(max_digits=10, decimal_places=2, default=0)
    currency         = CharField(max_length=3, default="usd")
    status           = CharField(max_length=20, choices=Status.choices)
    invoice_pdf      = URLField(blank=True)
    hosted_invoice_url = URLField(blank=True)
    period_start     = DateTimeField(null=True)
    period_end       = DateTimeField(null=True)

    class Meta:
        db_table = "billing_invoice"


class WebhookEvent(TimestampedModel):
    """Idempotency log of all processed Stripe webhook events."""
    stripe_event_id  = CharField(max_length=255, unique=True, db_index=True)
    event_type       = CharField(max_length=100)
    payload          = JSONField()
    processed_at     = DateTimeField(null=True, blank=True)
    error            = TextField(blank=True)

    class Meta:
        db_table = "billing_webhook_event"
```

#### `webhooks.py` — Event Router

```python
WEBHOOK_HANDLERS: dict[str, Callable] = {
    "checkout.session.completed":          handle_checkout_completed,
    "customer.subscription.created":       handle_subscription_created,
    "customer.subscription.updated":       handle_subscription_updated,
    "customer.subscription.deleted":       handle_subscription_deleted,
    "invoice.payment_succeeded":           handle_invoice_paid,
    "invoice.payment_failed":              handle_invoice_payment_failed,
    "customer.subscription.trial_will_end": handle_trial_ending,
}

def process_webhook(event: stripe.Event) -> None:
    """
    Entry point from WebhookView.
    1. Check WebhookEvent for idempotency (skip if already processed).
    2. Dispatch to the appropriate handler.
    3. Mark event as processed or log the error.
    """
```

#### `stripe_client.py`

```python
class StripeClient:
    """
    Thin wrapper providing:
    - create_checkout_session(team, plan, interval) → Session
    - create_customer_portal_session(team) → Session
    - create_or_get_customer(team) → Customer
    - cancel_subscription(subscription) → None
    - sync_subscription_from_stripe(stripe_sub_id) → Subscription
    """
```

#### `serializers.py`

| Serializer | Purpose |
|---|---|
| `PlanSerializer` | Public plan list (features, prices) |
| `SubscriptionSerializer` | Current team subscription status |
| `CheckoutSessionSerializer` | Input: plan_id, interval → Output: checkout_url |
| `CustomerPortalSerializer` | Output: portal_url |
| `InvoiceSerializer` | Invoice list for billing history |

#### `views.py`

| View | Method | Endpoint | Auth |
|---|---|---|---|
| `PlanListView` | GET | `/api/v1/billing/plans/` | No |
| `SubscriptionDetailView` | GET | `/api/v1/billing/subscription/` | Team member |
| `CheckoutView` | POST | `/api/v1/billing/checkout/` | Team owner |
| `CustomerPortalView` | POST | `/api/v1/billing/portal/` | Team owner |
| `InvoiceListView` | GET | `/api/v1/billing/invoices/` | Team admin+ |
| `WebhookView` | POST | `/api/v1/billing/webhook/` | Stripe sig |
| `CancelSubscriptionView` | POST | `/api/v1/billing/subscription/cancel/` | Team owner |

---

### 3.4 `api`

**Purpose:** DRF infrastructure — routing, versioning, throttling, pagination, exception handling, OpenAPI schema generation.

#### `router.py`

```python
router = DefaultRouter()

# Register all app ViewSets here — single source of truth for API routing
router.register(r"teams",                    TeamViewSet,                 basename="team")
router.register(r"teams/(?P<team_id>[^/.]+)/members",
                TeamMembershipViewSet,        basename="team-member")
router.register(r"teams/(?P<team_id>[^/.]+)/invitations",
                TeamInvitationViewSet,        basename="team-invitation")
```

#### `throttling.py`

```python
class BurstRateThrottle(UserRateThrottle):
    scope = "burst"         # 60/min — default for authenticated users

class SustainedRateThrottle(UserRateThrottle):
    scope = "sustained"     # 1000/day

class AnonBurstThrottle(AnonRateThrottle):
    scope = "anon_burst"    # 20/min for unauthenticated

class AuthEndpointThrottle(AnonRateThrottle):
    scope = "auth"          # 10/min — stricter for login/register to deter brute force
```

#### `pagination.py`

```python
class StandardResultsSetPagination(PageNumberPagination):
    page_size             = 20
    page_size_query_param = "page_size"
    max_page_size         = 100

class CursorResultsSetPagination(CursorPagination):
    page_size   = 20
    ordering    = "-created_at"   # Use for time-series lists (invoices, audit logs)
```

#### `exceptions.py`

```python
def shipyard_exception_handler(exc, context):
    """
    Wraps DRF's default handler.
    All error responses follow the shape:
    {
        "error": {
            "code":    "validation_error",
            "message": "Human-readable summary",
            "detail":  { ... field-level errors }
        }
    }
    """
```

#### `schema.py` — OpenAPI

```python
# drf-spectacular configuration
SPECTACULAR_SETTINGS = {
    "TITLE":       "Shipyard API",
    "DESCRIPTION": "SaaS Boilerplate API",
    "VERSION":     "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX":   "/api/v1/",
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
    },
}
```

Schema served at:
- `GET /api/v1/schema/` — raw OpenAPI JSON
- `GET /api/v1/schema/swagger-ui/` — Swagger UI
- `GET /api/v1/schema/redoc/` — Redoc UI

---

### 3.5 `core`

**Purpose:** Project-wide shared utilities — abstract base models, health check endpoints, S3 storage backends, custom middleware, shared validators.

#### `models.py` — Abstract Base Models

```python
class TimestampedModel(Model):
    """All Shipyard models inherit from this for created_at / updated_at."""
    created_at = DateTimeField(auto_now_add=True, db_index=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(TimestampedModel):
    """Adds UUID primary key on top of TimestampedModel."""
    id = UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True
```

#### `views.py` — Health Checks

```python
class HealthCheckView(APIView):
    """
    GET /health/
    Returns 200 always — suitable for load balancer liveness probe.
    {"status": "ok"}
    """
    permission_classes = [AllowAny]
    authentication_classes = []


class ReadinessView(APIView):
    """
    GET /ready/
    Checks DB and Redis connectivity.
    Returns 200 if all dependencies are reachable, 503 otherwise.
    {"status": "ok"|"degraded", "checks": {"db": "ok", "redis": "ok"}}
    """
    permission_classes = [AllowAny]
    authentication_classes = []
```

#### `storage.py`

```python
class PublicMediaStorage(S3Boto3Storage):
    """Public-read bucket for avatars, team logos."""
    location       = "media/public"
    default_acl    = "public-read"
    file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
    """Private bucket for sensitive documents — URL signing required."""
    location           = "media/private"
    default_acl        = "private"
    file_overwrite     = False
    custom_domain      = False

    def url(self, name):
        return self.connection.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": self._normalize_name(name)},
            ExpiresIn=3600,
        )
```

#### `middleware.py`

```python
class RequestIDMiddleware:
    """
    Injects a unique X-Request-ID header into every request and response.
    Used for log correlation and Sentry tracing.
    """

class CurrentTeamMiddleware:
    """
    Reads X-Team-ID header and attaches the resolved Team to request.team.
    Used by permission classes and views to avoid repeated DB lookups.
    """
```

---

### 3.6 `notifications`

**Purpose:** Transactional email delivery via Celery. All emails are subclasses of `BaseEmail`, rendered from Django templates, and dispatched through Celery to avoid blocking the request/response cycle.

#### `email.py`

```python
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
```

#### `tasks.py`

```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, email_class: str, to: str, context: dict) -> None:
    """
    Celery task wrapping BaseEmail.send().
    Retries 3× on failure with exponential backoff.
    Logs every send attempt to EmailLog.
    """

@shared_task
def send_welcome_email(user_id: str) -> None:
    """Convenience wrapper. Called from users.signals post_save."""

@shared_task
def send_verification_email(user_id: str) -> None:
    """Called after registration and from 'resend verification' endpoint."""
```

---

## 4. Infrastructure & Configuration Files

---

### 4.1 Docker & Compose

#### `docker/dev/Dockerfile`

```dockerfile
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements/base.txt requirements/development.txt ./requirements/
RUN pip install -r requirements/development.txt

COPY . .

ENTRYPOINT ["docker/dev/entrypoint.sh"]
```

#### `docker/prod/Dockerfile` (multi-stage)

```dockerfile
# ── Stage 1: builder ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements/base.txt requirements/production.txt ./requirements/
RUN pip install --prefix=/install -r requirements/production.txt

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash shipyard

COPY --from=builder /install /usr/local
WORKDIR /app

COPY --chown=shipyard:shipyard . .
RUN python manage.py collectstatic --noinput --settings=config.settings.production

USER shipyard
ENTRYPOINT ["docker/prod/entrypoint.sh"]
```

#### `docker-compose.yml` (development)

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    environment:
      POSTGRES_DB:       ${POSTGRES_DB:-shipyard}
      POSTGRES_USER:     ${POSTGRES_USER:-shipyard}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-shipyard}
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-shipyard}"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

  web:
    build:
      context: .
      dockerfile: docker/dev/Dockerfile
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    env_file: .env
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.development
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery:
    build:
      context: .
      dockerfile: docker/dev/Dockerfile
    command: celery -A config.celery worker -l INFO --concurrency=2
    volumes:
      - .:/app
    env_file: .env
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.development
    depends_on:
      - redis
      - db

  celery-beat:
    build:
      context: .
      dockerfile: docker/dev/Dockerfile
    command: celery -A config.celery beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - .:/app
    env_file: .env
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.development
    depends_on:
      - redis
      - db

  flower:
    build:
      context: .
      dockerfile: docker/dev/Dockerfile
    command: celery -A config.celery flower --port=5555
    ports:
      - "5555:5555"
    env_file: .env
    depends_on:
      - redis

volumes:
  postgres_data:
  redis_data:
```

#### `docker-compose.prod.yml` (production)

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB:       ${POSTGRES_DB}
      POSTGRES_USER:     ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data

  web:
    build:
      context: .
      dockerfile: docker/prod/Dockerfile
    restart: unless-stopped
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 60 --access-logfile - --error-logfile -
    env_file: .env
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    expose:
      - "8000"

  celery:
    build:
      context: .
      dockerfile: docker/prod/Dockerfile
    restart: unless-stopped
    command: celery -A config.celery worker -l WARNING --concurrency=4 -Q default,emails,billing
    env_file: .env
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.production
    depends_on:
      - redis
      - db

  celery-beat:
    build:
      context: .
      dockerfile: docker/prod/Dockerfile
    restart: unless-stopped
    command: celery -A config.celery beat -l WARNING --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file: .env
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.production
    depends_on:
      - redis
      - db

  nginx:
    image: nginx:1.25-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.prod.conf:/etc/nginx/conf.d/default.conf:ro
      - ./static:/var/www/static:ro
      - ./media:/var/www/media:ro
      - certbot_www:/var/www/certbot:ro
      - certbot_conf:/etc/letsencrypt:ro
    depends_on:
      - web

  certbot:
    image: certbot/certbot
    volumes:
      - certbot_www:/var/www/certbot
      - certbot_conf:/etc/letsencrypt
    # Run manually: docker compose -f docker-compose.prod.yml run --rm certbot certonly ...

volumes:
  postgres_data:
  redis_data:
  certbot_www:
  certbot_conf:
```

---

### 4.2 Nginx

#### `docker/nginx/nginx.prod.conf`

```nginx
upstream django {
    server web:8000;
}

# Redirect HTTP → HTTPS
server {
    listen 80;
    server_name example.com www.example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_session_cache   shared:SSL:10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Static files
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files (dev fallback; production uses S3)
    location /media/ {
        alias /var/www/media/;
        expires 1y;
    }

    # API rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;

    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass         http://django;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    # Django admin — restrict by IP in production
    location /admin/ {
        allow  10.0.0.0/8;    # Replace with your office/VPN CIDR
        deny   all;
        proxy_pass http://django;
        proxy_set_header Host            $host;
        proxy_set_header X-Real-IP       $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        proxy_pass         http://django;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

---

### 4.3 Celery

#### `config/celery.py`

```python
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("shipyard")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# ── Periodic Tasks (Celery Beat) ─────────────────────────────────────────────
app.conf.beat_schedule = {
    # Sync Stripe subscription statuses every hour
    "sync-stripe-subscriptions": {
        "task":     "apps.billing.tasks.sync_stripe_subscriptions",
        "schedule": crontab(minute=0),
    },
    # Clean up expired tokens daily at 3am UTC
    "cleanup-expired-tokens": {
        "task":     "apps.core.tasks.cleanup_expired_tokens",
        "schedule": crontab(hour=3, minute=0),
    },
    # Expire pending invitations daily at 3:30am UTC
    "expire-invitations": {
        "task":     "apps.teams.tasks.expire_pending_invitations",
        "schedule": crontab(hour=3, minute=30),
    },
}

# ── Queue Routing ─────────────────────────────────────────────────────────────
app.conf.task_routes = {
    "apps.notifications.tasks.*": {"queue": "emails"},
    "apps.billing.tasks.*":       {"queue": "billing"},
    "*":                          {"queue": "default"},
}

app.conf.task_serializer        = "json"
app.conf.result_serializer      = "json"
app.conf.accept_content         = ["json"]
app.conf.task_acks_late         = True
app.conf.worker_prefetch_multiplier = 1
```

---

### 4.4 GitHub Actions CI/CD

#### `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  PYTHON_VERSION: "3.12"

jobs:
  lint:
    name: Lint (ruff + mypy)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
      - run: pip install ruff mypy
      - run: ruff check .
      - run: ruff format --check .
      - run: mypy apps/ config/ --ignore-missing-imports

  test:
    name: Test (pytest)
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB:       shipyard_test
          POSTGRES_USER:     shipyard
          POSTGRES_PASSWORD: shipyard
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5
        ports: ["5432:5432"]
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5
        ports: ["6379:6379"]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
      - run: pip install -r requirements/development.txt
      - name: Run tests
        env:
          DJANGO_SETTINGS_MODULE: config.settings.testing
          DATABASE_URL: postgres://shipyard:shipyard@localhost:5432/shipyard_test
          REDIS_URL:    redis://localhost:6379/0
          SECRET_KEY:   ci-test-secret-key-not-for-production
        run: |
          pytest --cov=apps --cov-report=xml --cov-report=term-missing -v
      - uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
```

#### `.github/workflows/build.yml`

```yaml
name: Build & Push

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          file:    docker/prod/Dockerfile
          push:    true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to:   type=gha,mode=max
```

#### `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host:     ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key:      ${{ secrets.DEPLOY_SSH_KEY }}
          script: |
            cd /opt/shipyard
            git pull origin main
            docker compose -f docker-compose.prod.yml pull
            docker compose -f docker-compose.prod.yml up -d --remove-orphans
            docker compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput
            docker system prune -f
```

---

## 5. Environment Variables

#### `.env.example`

```bash
# ── Django ────────────────────────────────────────────────────────────────────
SECRET_KEY=change-me-generate-with-python-secrets-token-hex-50
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.development

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL=postgres://shipyard:shipyard@localhost:5432/shipyard

# ── Redis ─────────────────────────────────────────────────────────────────────
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# ── Celery ────────────────────────────────────────────────────────────────────
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourapp.com
SUPPORT_EMAIL=support@yourapp.com

# ── Stripe ────────────────────────────────────────────────────────────────────
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# ── Social Auth ───────────────────────────────────────────────────────────────
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# ── AWS / S3 ──────────────────────────────────────────────────────────────────
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=

# ── Sentry ────────────────────────────────────────────────────────────────────
SENTRY_DSN=
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=0.1

# ── Frontend ──────────────────────────────────────────────────────────────────
FRONTEND_URL=http://localhost:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# ── JWT ───────────────────────────────────────────────────────────────────────
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=30
```

### Environment Variables Reference Table

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | Yes | — | Django secret key. Use `python -c "import secrets; print(secrets.token_hex(50))"` |
| `DEBUG` | Yes | `False` | Never `True` in production |
| `ALLOWED_HOSTS` | Yes | — | Comma-separated list of allowed host names |
| `DATABASE_URL` | Yes | — | PostgreSQL connection DSN |
| `REDIS_URL` | Yes | — | Redis connection URL |
| `CELERY_BROKER_URL` | Yes | — | Same as `REDIS_URL` unless using separate Redis |
| `STRIPE_SECRET_KEY` | Yes | — | Stripe API secret key (`sk_live_...` in prod) |
| `STRIPE_WEBHOOK_SECRET` | Yes | — | Webhook signing secret from Stripe Dashboard |
| `SENTRY_DSN` | No | — | Leave empty to disable Sentry |
| `AWS_ACCESS_KEY_ID` | No | — | Required only if `DEFAULT_FILE_STORAGE` is S3 |
| `FRONTEND_URL` | Yes | — | Used to build email links (verification, reset) |
| `CORS_ALLOWED_ORIGINS` | Yes | — | Comma-separated origins for CORS headers |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | No | `60` | JWT access token expiry |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | No | `30` | JWT refresh token expiry |
| `GOOGLE_CLIENT_ID` | No | — | Required to enable Google social auth |
| `GITHUB_CLIENT_ID` | No | — | Required to enable GitHub social auth |

---

## 6. API Design

### URL Structure

```
/health/                                      # Liveness probe
/ready/                                       # Readiness probe
/admin/                                       # Django Admin (Unfold)
/api/v1/                                      # API root
/api/v1/schema/                               # OpenAPI schema
/api/v1/schema/swagger-ui/                    # Swagger UI
/api/v1/schema/redoc/                         # Redoc

# Auth
/api/v1/auth/register/
/api/v1/auth/login/
/api/v1/auth/logout/
/api/v1/auth/token/refresh/
/api/v1/auth/verify-email/
/api/v1/auth/me/
/api/v1/auth/password/change/
/api/v1/auth/password/reset/
/api/v1/auth/password/reset/confirm/
/api/v1/auth/social/{provider}/

# Teams
/api/v1/teams/                                # List owned/member teams, create team
/api/v1/teams/{id}/                           # Retrieve, update, delete team
/api/v1/teams/{id}/members/                   # List members
/api/v1/teams/{id}/members/{id}/              # Update role, remove member
/api/v1/teams/{id}/invitations/               # List, create invitations
/api/v1/teams/{id}/invitations/{id}/          # Revoke invitation
/api/v1/invitations/accept/                   # Accept an invitation by token

# Billing
/api/v1/billing/plans/                        # List available plans
/api/v1/billing/subscription/                 # Current team subscription
/api/v1/billing/subscription/cancel/          # Cancel at period end
/api/v1/billing/checkout/                     # Create Stripe Checkout session
/api/v1/billing/portal/                       # Create Stripe Customer Portal session
/api/v1/billing/invoices/                     # Invoice history
/api/v1/billing/webhook/                      # Stripe webhook receiver
```

### Response Envelope

All API responses use a consistent envelope format:

```json
// Success (single object)
{
  "data": { ... },
  "meta": {}
}

// Success (list)
{
  "data": [ ... ],
  "meta": {
    "count": 42,
    "next": "https://api.example.com/api/v1/teams/?page=2",
    "previous": null
  }
}

// Error
{
  "error": {
    "code":    "validation_error",
    "message": "Invalid input data.",
    "detail":  {
      "email": ["Enter a valid email address."]
    }
  }
}
```

### Authentication Header

```
Authorization: Bearer <access_token>
```

JWT access tokens expire in 60 minutes by default. Obtain a new access token using the refresh token at `/api/v1/auth/token/refresh/`.

---

## 7. Data Models — Entity Relationship Overview

```
User ─────────────────────────────────────────────────────
  │  id (UUID PK)
  │  email (unique)
  │  full_name
  │  stripe_customer_id
  │  is_email_verified
  │
  ├── TeamMembership (through table)
  │     user → User
  │     team → Team
  │     role: owner | admin | member
  │
  └── EmailVerificationToken
  └── PasswordResetToken

Team ─────────────────────────────────────────────────────
  │  id (UUID PK)
  │  name, slug
  │  owner → User
  │  stripe_customer_id
  │  max_members, max_projects (denormalized from Plan)
  │
  ├── TeamMembership (members)
  ├── TeamInvitation
  ├── Subscription (OneToOne)
  └── Invoice (many)

Plan ─────────────────────────────────────────────────────
  │  id (UUID PK)
  │  name, slug
  │  stripe_product_id
  │  stripe_price_id_monthly, stripe_price_id_yearly
  │  price_monthly, price_yearly
  │  max_members, max_projects, has_api_access, ...
  │
  └── Subscription (many)

Subscription ─────────────────────────────────────────────
  │  team (OneToOne)
  │  plan → Plan
  │  status: trialing | active | past_due | cancelled | ...
  │  stripe_subscription_id
  │  current_period_start, current_period_end

Invoice ──────────────────────────────────────────────────
  │  team → Team
  │  stripe_invoice_id
  │  amount_due, amount_paid
  │  status: draft | open | paid | void

WebhookEvent ─────────────────────────────────────────────
  │  stripe_event_id (unique — idempotency key)
  │  event_type
  │  payload (JSON)
  │  processed_at

EmailLog ─────────────────────────────────────────────────
       to, subject, email_class
       sent_at, status, error
```

---

## 8. Authentication Flow

### Email/Password Registration

```
1. POST /api/v1/auth/register/       { email, full_name, password, password_confirm }
2. Server creates User (is_email_verified=False)
3. post_save signal → send_verification_email.delay(user.id)
4. Response: 201 { data: { user: {...} } }

5. User clicks link in email → GET /verify?token=<token>
6. Frontend POSTs token: POST /api/v1/auth/verify-email/  { token }
7. Server sets is_email_verified=True, marks token used
8. Response: 200 { message: "Email verified." }
```

### JWT Login

```
1. POST /api/v1/auth/login/          { email, password }
2. Validate credentials
3. Response: 200 {
     data: {
       access:  "<JWT access token>",
       refresh: "<JWT refresh token>",
       user:    { id, email, full_name, ... }
     }
   }

4. Client stores tokens (httpOnly cookie recommended for web)
5. Authenticated requests: Authorization: Bearer <access>
6. Access expires → POST /api/v1/auth/token/refresh/ { refresh }
7. Response: 200 { data: { access: "<new access token>" } }
```

### Social Auth (Google / GitHub)

```
1. Frontend initiates OAuth flow → redirected to provider
2. Provider returns authorization code to callback URL
3. Frontend POSTs code: POST /api/v1/auth/social/google/ { code }
4. Server exchanges code for provider tokens via allauth SocialAccountAdapter
5. If new user: User created, welcome email queued
6. Response: 200 { data: { access, refresh, user } }
```

---

## 9. Stripe Integration Flow

### New Subscription (Checkout)

```
1. Team owner: POST /api/v1/billing/checkout/  { plan_id, interval: "month"|"year" }
2. Server: StripeClient.create_checkout_session(team, plan, interval)
   - Creates/retrieves Stripe Customer for team.stripe_customer_id
   - Creates Checkout Session with:
       success_url = FRONTEND_URL/billing/success?session_id={CHECKOUT_SESSION_ID}
       cancel_url  = FRONTEND_URL/billing/plans
       client_reference_id = team.id  (used to identify team in webhook)
3. Response: 200 { data: { checkout_url: "https://checkout.stripe.com/..." } }
4. Frontend redirects user to checkout_url

5. User completes payment on Stripe hosted page
6. Stripe fires webhook → POST /api/v1/billing/webhook/
7. WebhookView:
   a. Verify signature (stripe.Webhook.construct_event)
   b. Check WebhookEvent table for idempotency
   c. Dispatch to handle_checkout_completed()
      - Creates/updates Subscription record
      - Updates Team.max_members, Team.max_projects from Plan limits
      - Queues subscription confirmation email
```

### Customer Portal (Manage Billing)

```
1. Team owner: POST /api/v1/billing/portal/
2. Server: StripeClient.create_customer_portal_session(team)
3. Response: 200 { data: { portal_url: "https://billing.stripe.com/..." } }
4. Frontend redirects to portal_url
5. User manages payment methods, views invoices, cancels via Stripe UI
6. Any changes → Stripe fires webhooks → handled automatically
```

### Webhook Events Handled

| Stripe Event | Handler Action |
|---|---|
| `checkout.session.completed` | Create Subscription, update Team limits, send confirmation email |
| `customer.subscription.updated` | Update Subscription status/plan, sync Team limits |
| `customer.subscription.deleted` | Set Subscription.status=cancelled, downgrade Team limits |
| `invoice.payment_succeeded` | Create Invoice record, send receipt email |
| `invoice.payment_failed` | Set Subscription.status=past_due, send billing alert email |
| `customer.subscription.trial_will_end` | Send trial ending reminder email (3 days before) |

---

## 10. Celery Task Architecture

### Queues

| Queue | Workers | Tasks |
|---|---|---|
| `default` | 2-4 | General async tasks |
| `emails` | 1-2 | All email sends (serialized to respect SMTP/SES rate limits) |
| `billing` | 1 | Stripe sync, billing alerts (serialized to avoid race conditions) |

### Periodic Tasks (Beat)

| Task | Schedule | Description |
|---|---|---|
| `billing.tasks.sync_stripe_subscriptions` | Hourly | Reconcile local Subscription records with Stripe |
| `core.tasks.cleanup_expired_tokens` | Daily 03:00 UTC | Delete expired verification + reset tokens |
| `teams.tasks.expire_pending_invitations` | Daily 03:30 UTC | Mark stale invitations as expired |
| `billing.tasks.send_trial_ending_alerts` | Daily 10:00 UTC | Find trials ending in 3 days, queue alert emails |

### Key Tasks

```python
# notifications/tasks.py
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, email_class, to, context):
    """Retry 3× with 1-minute delay on failure."""

# billing/tasks.py
@shared_task
def sync_stripe_subscriptions():
    """Fetch all active Stripe subscriptions and reconcile with DB."""

# core/tasks.py
@shared_task
def cleanup_expired_tokens():
    """Hard-delete tokens past their expiry + 7-day grace period."""
```

### Flower Monitoring

Flower is available at `http://localhost:5555` in development.  
In production, put Flower behind Nginx with HTTP Basic Auth:

```nginx
location /flower/ {
    auth_basic           "Flower";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass           http://flower:5555/;
}
```

---

## 11. README Template

The following is the template content for the project's `README.md`:

---

```markdown
# Shipyard — Django SaaS Boilerplate

Production-ready Django SaaS boilerplate. Stop rebuilding auth, billing, and multi-tenancy
from scratch. Ship your SaaS in days, not months.

## Features

### Authentication & Users
- Custom User model (email-based, no username)
- JWT + session authentication
- Email verification flow
- Password reset flow
- Social auth: Google, GitHub (via django-allauth)

### Multi-Tenancy
- Team/Organization model
- Role-based access: owner, admin, member
- Team invitations via email
- Per-team resource limits enforced by plan

### Billing (Stripe)
- Plan catalog with monthly/yearly pricing
- Stripe Checkout hosted payment page
- Stripe Customer Portal (manage payment methods, cancel)
- Webhook handling with idempotency
- Invoice history
- Per-tenant feature limits tied to plan

### API
- Django REST Framework, API-first
- Versioned endpoints: `/api/v1/`
- JWT Bearer authentication
- Rate throttling (burst + sustained)
- Cursor + page-number pagination
- OpenAPI 3.0 schema (Swagger UI + Redoc)
- Consistent JSON error envelope

### Background Tasks
- Celery + Beat with Redis broker
- Separate queues: default, emails, billing
- Flower monitoring dashboard
- Retry logic with exponential backoff

### Email
- Transactional emails: welcome, verification, password reset, invitations, billing alerts
- HTML + plain text templates
- Celery-queued (non-blocking)
- Audit log of every sent email

### Infrastructure
- Docker Compose: separate dev + production configs
- Multi-stage production Dockerfile (minimal attack surface)
- Nginx: SSL termination, static files, rate limiting, security headers
- Gunicorn with worker + thread configuration
- PostgreSQL 16 with UUID extension
- Redis for cache, sessions, and Celery broker

### Developer Experience
- GitHub Actions: lint (ruff), type check (mypy), test (pytest), build, deploy
- Pre-commit hooks: ruff, black, isort, mypy
- django-environ for `.env` management
- Comprehensive test suite with factory_boy fixtures
- Makefile with common commands

### Observability
- Sentry error tracking + performance monitoring
- Health check endpoints (`/health/`, `/ready/`)
- Request ID middleware for log correlation
- Structured logging

### Admin
- django-unfold enhanced admin interface
- All models registered with search, filters, and list display

## Quick Start

### Prerequisites
- Docker + Docker Compose
- Python 3.12+ (for local development without Docker)

### 1. Clone and configure

```bash
git clone https://github.com/your-org/shipyard.git
cd shipyard
cp .env.example .env
# Edit .env with your values (see Environment Variables section)
```

### 2. Start the development stack

```bash
make dev
# Equivalent to: docker compose up --build
```

This starts: PostgreSQL, Redis, Django (hot reload), Celery worker, Celery Beat, Flower.

### 3. Run migrations and create superuser

```bash
make migrate          # python manage.py migrate
make superuser        # python manage.py createsuperuser
make seed             # Optional: populate sample data
```

### 4. Access the services

| Service | URL |
|---|---|
| Django API | http://localhost:8000/api/v1/ |
| Swagger UI | http://localhost:8000/api/v1/schema/swagger-ui/ |
| Django Admin | http://localhost:8000/admin/ |
| Flower | http://localhost:5555/ |

## Project Structure

```
shipyard/
├── apps/
│   ├── users/          Custom User model, JWT auth, social auth
│   ├── teams/          Multi-tenancy, roles, invitations
│   ├── billing/        Stripe subscriptions, webhooks, invoices
│   ├── api/            DRF router, throttling, pagination, schema
│   ├── core/           Shared models, health checks, storage, middleware
│   └── notifications/  Transactional emails, Celery tasks
├── config/
│   ├── settings/       base.py, development.py, production.py, testing.py
│   ├── celery.py       Celery app + Beat schedule
│   └── urls.py         Root URL config
├── docker/             Dev + prod Dockerfiles, Nginx config
├── docs/               Deployment guide, API reference, setup guides
├── requirements/       base.txt, development.txt, production.txt
└── tests/              Integration tests + fixtures
```

## Environment Variables

See `.env.example` for a complete template. Key variables:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key (generate with `python -c "import secrets; print(secrets.token_hex(50))"`) |
| `DATABASE_URL` | PostgreSQL DSN (e.g. `postgres://user:pass@host:5432/db`) |
| `REDIS_URL` | Redis URL (e.g. `redis://localhost:6379/0`) |
| `STRIPE_SECRET_KEY` | Stripe API key |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret |
| `SENTRY_DSN` | Sentry DSN (leave empty to disable) |
| `FRONTEND_URL` | Used in email links |
| `CORS_ALLOWED_ORIGINS` | Comma-separated allowed origins |

## Stripe Setup

1. Create a Stripe account at https://stripe.com
2. Create Products and Prices in the Stripe Dashboard — one per plan (Starter, Pro, Enterprise)
3. Copy price IDs into the `Plan` model via Django Admin
4. Configure webhook endpoint: `https://yourapp.com/api/v1/billing/webhook/`
   - Events to subscribe: `checkout.session.completed`, `customer.subscription.*`, `invoice.*`
5. Copy webhook signing secret to `STRIPE_WEBHOOK_SECRET`

## Deployment

### Production with Docker Compose

```bash
# On your server (first deploy)
git clone https://github.com/your-org/shipyard.git /opt/shipyard
cd /opt/shipyard
cp .env.example .env
# Fill in production values

# Start the stack
docker compose -f docker-compose.prod.yml up -d

# Run migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### SSL with Let's Encrypt

```bash
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot --webroot-path /var/www/certbot \
  -d example.com -d www.example.com \
  --email admin@example.com --agree-tos --no-eff-email
```

Add a cron job to renew certificates:

```cron
0 0 * * * docker compose -f /opt/shipyard/docker-compose.prod.yml run --rm certbot renew
```

### GitHub Actions Automated Deploy

1. Add repository secrets: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`
2. Create a GitHub release with a version tag (e.g. `v1.2.0`)
3. The `deploy.yml` workflow pulls the new image and restarts services automatically

## Running Tests

```bash
make test              # pytest with coverage
make test-fast         # pytest -x (stop on first failure)
make coverage          # open htmlcov/index.html
```

## Common Makefile Targets

```
make dev               Start development stack
make down              Stop all containers
make migrate           Run database migrations
make makemigrations    Create new migration files
make superuser         Create Django superuser
make shell             Django shell_plus
make test              Run test suite
make lint              Run ruff + mypy
make format            Run ruff format + isort
make seed              Populate sample data
make logs              Tail all container logs
make db-shell          Connect to PostgreSQL
```

## License

This software is licensed for use under the Shipyard Commercial License.
See `LICENSE` for terms. Do not redistribute.
```

---

## Appendix: `requirements/base.txt`

```
Django==5.1.*
djangorestframework==3.15.*
djangorestframework-simplejwt==5.3.*
drf-spectacular==0.27.*
django-filter==24.*
django-environ==0.11.*
django-allauth[socialaccount]==64.*
django-unfold==0.38.*
django-storages[s3]==1.14.*
django-cors-headers==4.*
django-celery-beat==2.7.*
celery[redis]==5.4.*
flower==2.0.*
psycopg[binary]==3.*
redis==5.*
stripe==10.*
sentry-sdk[django]==2.*
Pillow==10.*
gunicorn==22.*
```

## Appendix: `requirements/development.txt`

```
-r base.txt
pytest==8.*
pytest-django==4.*
pytest-cov==5.*
pytest-xdist==3.*
factory-boy==3.*
faker==26.*
responses==0.25.*
freezegun==1.*
ipython==8.*
django-extensions==3.*
watchdog==4.*
ruff==0.5.*
mypy==1.11.*
django-stubs==5.*
djangorestframework-stubs==3.*
pre-commit==3.*
```

## Appendix: `pyproject.toml` (tool configuration)

```toml
[tool.ruff]
line-length    = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "DJ"]
ignore = ["DJ001"]   # Allow nullable CharField (used intentionally)

[tool.mypy]
python_version     = "3.12"
strict             = true
ignore_missing_imports = true
plugins = ["mypy_django_plugin.main", "mypy_drf_plugin.main"]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.testing"
python_files   = ["test_*.py"]
addopts        = "--reuse-db -v"
testpaths      = ["apps", "tests"]

[tool.coverage.run]
source   = ["apps"]
omit     = ["*/migrations/*", "*/tests/*", "*/admin.py"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```
