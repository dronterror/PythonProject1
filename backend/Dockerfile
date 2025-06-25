# Simplified Poetry-based FastAPI application
FROM python:3.11-slim

# Python and Poetry configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Configure Poetry: don't create virtual env (install globally in container)
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Copy Poetry configuration
COPY pyproject.toml poetry.lock* ./

# Install dependencies directly in this stage
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-root && \
    rm -rf $POETRY_CACHE_DIR

# Copy application source code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --no-create-home appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Use direct uvicorn command since dependencies are installed globally
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 