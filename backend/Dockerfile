# Multi-stage build for faster builds and smaller images
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Set environment variables for performance
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--workers", "1"]

# Production stage with Gunicorn
FROM base as production
COPY . .

# Add wait-for-it script before user change
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app && \
    chown appuser:appuser /wait-for-it.sh
USER appuser

EXPOSE 8000

# Use Gunicorn with Uvicorn workers for production
CMD ["/wait-for-it.sh", "db:5432", "--", "gunicorn", "main:app", "-c", "gunicorn.conf.py"] 