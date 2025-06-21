# ValMed Quick Start Guide

## 🚀 Fast Build Options

### Option 1: Windows (Recommended)
```bash
# Run the optimized build script
build.bat
```

### Option 2: Linux/Mac
```bash
# Make script executable and run
chmod +x build.sh
./build.sh
```

### Option 3: Manual Docker Compose
```bash
# Development mode (faster builds, hot reload)
docker-compose -f docker-compose.dev.yml up --build

# Production mode
docker-compose up --build
```

## ⚡ Build Optimizations Implemented

### 1. **Multi-Stage Docker Builds**
- Separate development and production stages
- Cached dependency layers
- Smaller final images

### 2. **Build Caching**
- Docker layer caching
- Angular build cache
- Python pip cache
- Node modules caching

### 3. **Parallel Processing**
- Concurrent service builds
- Optimized dependency installation
- Reduced build context with .dockerignore

### 4. **Simplified Airflow**
- LocalExecutor instead of CeleryExecutor
- Removed Redis dependency
- Faster startup times

### 5. **Angular Optimizations**
- Build cache enabled
- Optimized production builds
- Reduced bundle sizes

## 📊 Expected Build Time Improvements

| Component | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Backend | 3-5 min | 1-2 min | 60-70% |
| Frontend | 4-6 min | 2-3 min | 50-60% |
| Airflow | 2-3 min | 1 min | 60-70% |
| **Total** | **9-14 min** | **4-6 min** | **60-70%** |

## 🔧 Development Workflow

### Hot Reload Development
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Frontend changes auto-reload at http://localhost:4200
# Backend changes auto-reload at http://localhost/api
```

### Production Build
```bash
# Build production images
docker-compose build --target production

# Start production environment
docker-compose up -d
```

## 🛠️ Troubleshooting

### Clear Build Cache
```bash
# Clear all caches
docker system prune -a
docker volume prune

# Clear specific caches
docker volume rm valmed_backend_cache valmed_frontend_cache
```

### Rebuild Specific Service
```bash
# Rebuild only backend
docker-compose build backend

# Rebuild only frontend
docker-compose build frontend
```

### Check Build Performance
```bash
# Monitor build progress
docker-compose build --progress=plain

# Check image sizes
docker images | grep valmed
```

## 🌐 Access Points

After successful build:
- **Frontend**: http://localhost
- **Backend API**: http://localhost/api
- **API Documentation**: http://localhost/api/docs
- **Traefik Dashboard**: http://localhost:8081
- **Airflow**: http://localhost:8080

## 📝 Environment Variables

Create `.env` file for custom configuration:
```env
# Database
POSTGRES_USER=valmed
POSTGRES_PASSWORD=valmedpass
POSTGRES_DB=valmed

# Backend
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql+psycopg2://valmed:valmedpass@db:5432/valmed

# Airflow
AIRFLOW_UID=50000
```

## 🎯 Tips for Faster Development

1. **Use Development Mode**: Always use `docker-compose.dev.yml` for development
2. **Leverage Caching**: Don't clear caches unless necessary
3. **Parallel Builds**: Use `--parallel` flag for multiple services
4. **Selective Rebuilds**: Only rebuild changed services
5. **Volume Mounts**: Use volume mounts for hot reloading

## 🔍 Monitoring

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f [service-name]

# Monitor resources
docker stats
``` 