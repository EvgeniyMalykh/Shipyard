# Shipyard

[![Python 3.12](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3120/)
[![Django 5.0](https://img.shields.io/badge/django-5.0-092E20?logo=django&logoColor=white)](https://docs.djangoproject.com/en/5.0/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15-red)](https://www.django-rest-framework.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Django SaaS Boilerplate. Ship faster.**

Shipyard gives you a production-ready Django backend with multi-tenancy, Stripe billing, async tasks, and a fully containerized dev environment — so you can focus on your product instead of scaffolding.

---

## What's Included

| Module | What you get |
|---|---|
| **Authentication** | JWT-based login/register, token refresh, email-based auth with UUID primary keys |
| **Teams** | Full multi-tenancy — create teams, invite members, manage roles via `TeamMembership` |
| **Billing** | Stripe-ready models: `Plan`, `Subscription`, `Invoice`, `WebhookEvent` |
| **Async Tasks** | Celery 5 + Celery Beat + Flower dashboard, DB-backed periodic tasks |
| **Notifications** | `EmailLog` model for outbound email tracking |
| **Base Models** | `TimestampedModel` and `UUIDModel` mixins |
| **Docker Stack** | Single `docker compose up` spins up all 6 services |
| **REST API** | DRF with versioned endpoints, CORS configured |

---

## Quick Start

```bash
git clone https://github.com/EvgeniyMalykh/Shipyard.git
cd Shipyard
cp .env.example .env
docker compose up --build
docker compose exec web python manage.py createsuperuser
```

| Service | URL |
|---|---|
| Django API | http://localhost:8000 |
| Django Admin | http://localhost:8000/admin |
| Flower | http://localhost:5555 |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Django 5.0.6 |
| REST API | Django REST Framework 3.15 |
| Auth | djangorestframework-simplejwt |
| Database | PostgreSQL 16 |
| Cache / Broker | Redis 7 |
| Task queue | Celery 5 + Celery Beat + Flower |
| Containerization | Docker + Docker Compose |

---

## API Overview

All endpoints prefixed with `/api/v1/`.

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register/` | Create account |
| `POST` | `/auth/login/` | Get JWT tokens |
| `POST` | `/auth/refresh/` | Refresh token |

### Users
| Method | Endpoint | Description |
|---|---|---|
| `GET/PATCH` | `/users/me/` | Profile |
| `POST` | `/users/me/password/` | Change password |

### Teams
| Method | Endpoint | Description |
|---|---|---|
| `GET/POST` | `/teams/` | List / create |
| `GET/PUT/DELETE` | `/teams/<id>/` | Detail |
| `GET` | `/teams/<id>/members/` | Members |
| `POST` | `/teams/<id>/invite/` | Invite |

### Billing
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/billing/plans/` | Plans |
| `GET` | `/billing/subscription/` | Current subscription |
| `GET` | `/billing/invoices/` | Invoices |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | Yes | `True` / `False` |
| `DATABASE_URL` | Yes | `postgres://user:pass@db:5432/shipyard` |
| `REDIS_URL` | Yes | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Yes | Same as `REDIS_URL` |
| `DJANGO_SETTINGS_MODULE` | Yes | `config.settings.development` |

---

## License

MIT. You own the code. No runtime license checks, no lock-in.
