# Frontend Dockerfile for Streamlit Dashboard
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (curl for health checks)
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
COPY services/frontend/pyproject.toml ./

# Copy frontend source code
COPY services/__init__.py ./services/
COPY services/frontend/ ./services/frontend/

# Install dependencies
RUN uv pip install --system .

# Expose Streamlit port
EXPOSE 8501

# Health check for Streamlit
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "services/frontend/src/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
