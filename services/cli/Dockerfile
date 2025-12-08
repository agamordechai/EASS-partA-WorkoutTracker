# CLI Dockerfile for operational tasks
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    PYTHONPATH=/app

# Copy service-specific pyproject.toml
COPY services/cli/pyproject.toml ./

# Copy CLI source code (CLI uses frontend client for API calls)
COPY services/__init__.py ./services/
COPY services/cli/ ./services/cli/
COPY services/frontend/ ./services/frontend/

# Install dependencies
RUN uv pip install --system .

# Default command shows help
CMD ["python", "-m", "services.cli.src.cli", "--help"]
