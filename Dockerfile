# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY manage.py ./
COPY sitebuilder ./sitebuilder/
COPY tests ./tests/

# Install dependencies
RUN uv pip install --no-cache -r pyproject.toml

# Create directory for data
RUN mkdir -p /app/var

# Expose Django development server port
EXPOSE 8000

# Default command (can be overridden in compose.yaml)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
