# syntax=docker/dockerfile:1
# Use Astral UV image as a development-friendly base per project docs
FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

# Accept UID/GID at build time (defaults to 1000) and expose as env vars.
ARG UID=1000
ARG GID=1000
ENV UID=${UID} \
    GID=${GID} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy

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

# Create workspace directory and ensure ownership
RUN mkdir -p /workspace/var \
    && mkdir -p /workspace/.venv \
    && chown -R appuser:appgroup /workspace

# Set working directory to /workspace which pairs well with UV tooling
WORKDIR /workspace

# Use BuildKit cache to speed uv operations across builds. We copy only
# pyproject.toml so uv can resolve dependencies and prime its cache.
# This step runs as root so it can populate /root/.cache/uv which is
# mounted as a cache during build.
USER root
COPY pyproject.toml /workspace/pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    sh -c 'uv sync --non-interactive --yes || true'

# Remove the copied metadata to avoid duplicating sources in the image layer
RUN rm -f /workspace/pyproject.toml || true

# Switch to non-root user for runtime
USER appuser

# Expose Django development server port
EXPOSE 8000

# Default command (can be overridden in compose.yaml)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
