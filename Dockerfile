# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Accept UID/GID at build time (defaults to 1000) and expose as env vars.
ARG UID=1000
ARG GID=1000
ENV UID=${UID} \
    GID=${GID} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    libpq-dev \
    build-essential \
    openssh-client \
    passwd \
    && rm -rf /var/lib/apt/lists/*

# Create group and user with specified IDs
RUN groupadd -g "${GID}" appgroup || true \
    && useradd -m -u "${UID}" -g appgroup -s /bin/sh appuser || true

# Create application directory and ensure ownership
RUN mkdir -p /app/var \
    && chown -R appuser:appgroup /app

# Switch to non-root user before setting WORKDIR
USER appuser

# Set working directory
WORKDIR /app

# Expose Django development server port
EXPOSE 8000

# Default command (can be overridden in compose.yaml)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
