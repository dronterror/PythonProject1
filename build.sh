#!/bin/bash

# ValMed Fast Build Script
# This script optimizes the build process for faster development

set -e

echo "🚀 Starting optimized ValMed build..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build cache images for faster subsequent builds
echo "📦 Building cache images..."
docker build --target development -t valmed-backend:cache ./backend || true
docker build --target development -t valmed-frontend:cache ./frontend || true

# Build with cache and parallel processing
echo "🔨 Building services with optimizations..."
docker-compose build --parallel --build-arg BUILDKIT_INLINE_CACHE=1

# Start services with health checks
echo "🚀 Starting services..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
docker-compose exec -T db pg_isready -U valmed || sleep 10

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose exec -T backend python -c "
from database import engine, Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
" || echo "⚠️ Database migration failed, but continuing..."

echo "✅ Build completed! Services are starting up..."
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost"
echo "   Backend API: http://localhost/api"
echo "   API Docs: http://localhost/api/docs"
echo "   Traefik Dashboard: http://localhost:8081"
echo "   Airflow: http://localhost:8080"
echo ""
echo "📊 Monitor services:"
echo "   docker-compose ps"
echo "   docker-compose logs -f [service-name]" 