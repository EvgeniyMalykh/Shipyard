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

RUN chmod +x docker/dev/entrypoint.sh
ENTRYPOINT ["docker/dev/entrypoint.sh"]