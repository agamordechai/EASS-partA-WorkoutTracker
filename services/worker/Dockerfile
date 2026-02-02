# Worker Service Dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Set Python environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install Python dependencies using uv
RUN uv pip install --system \
    arq \
    redis \
    httpx \
    pydantic \
    pydantic-settings \
    fastapi \
    uvicorn

# Copy shared services module
COPY services/__init__.py /app/services/

# Copy scripts (needed for refresh.py imports)
COPY scripts/refresh.py /app/scripts/

# Copy worker service
COPY services/worker/ /app/services/worker/

# Expose health check port
EXPOSE 8002

# Run worker
CMD ["python", "-m", "services.worker.src.worker"]
