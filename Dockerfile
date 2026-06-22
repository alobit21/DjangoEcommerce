FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
RUN cp -R media media_seed 2>/dev/null || true

# Collect static files at build time with a dummy key
RUN SECRET_KEY=build-time-dummy-key \
    DEBUG=False \
    DB_NAME="" \
    python manage.py collectstatic --noinput

EXPOSE 8000