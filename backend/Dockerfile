
# Multi-stage build for optimized image size
FROM python:3.10-slim AS builder

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.10-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install packages globally (not --user)
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Download spaCy model (with fallback options)
RUN python -m spacy download en_core_web_sm || \
    (pip install --no-cache-dir https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl || \
     python -m spacy.cli download en_core_web_sm || \
     echo "Warning: spaCy model download failed, will attempt at runtime")

# Copy application code
COPY app ./app

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs \
    /app/storage/resumes \
    /app/trained_models \
    /app/training_data

# Create non-root user and change ownership
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    chown -R appuser:appuser /app

# Copy trained models if they exist (optional - can be mounted as volume instead)
# COPY trained_models ./trained_models

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command: Use Gunicorn with Uvicorn workers for production
# For development, override with: docker run ... uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
CMD ["gunicorn", \
     "app.main:app", \
     "-w", "4", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
