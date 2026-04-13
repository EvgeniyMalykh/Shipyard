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