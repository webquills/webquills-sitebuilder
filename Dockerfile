# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
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
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create directory for data
RUN mkdir -p /app/var

# Expose Django development server port
EXPOSE 8000

# Default command (can be overridden in compose.yaml)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
