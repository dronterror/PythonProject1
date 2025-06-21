@echo off
REM ValMed Fast Build Script for Windows
REM This script optimizes the build process for faster development

echo 🚀 Starting optimized ValMed build...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Build cache images for faster subsequent builds
echo 📦 Building cache images...
docker build --target development -t valmed-backend:cache ./backend 2>nul || echo Cache build failed, continuing...
docker build --target development -t valmed-frontend:cache ./frontend 2>nul || echo Cache build failed, continuing...

REM Build with cache and parallel processing
echo 🔨 Building services with optimizations...
docker-compose build --parallel --build-arg BUILDKIT_INLINE_CACHE=1

REM Start services with health checks
echo 🚀 Starting services...
docker-compose up -d

REM Wait for database to be ready
echo ⏳ Waiting for database to be ready...
timeout /t 10 /nobreak >nul

REM Run database migrations
echo 🗄️ Running database migrations...
docker-compose exec -T backend python -c "from database import engine, Base; Base.metadata.create_all(bind=engine); print('Database tables created successfully')" 2>nul || echo ⚠️ Database migration failed, but continuing...

echo ✅ Build completed! Services are starting up...
echo.
echo 🌐 Access your application:
echo    Frontend: http://localhost
echo    Backend API: http://localhost/api
echo    API Docs: http://localhost/api/docs
echo    Traefik Dashboard: http://localhost:8081
echo    Airflow: http://localhost:8080
echo.
echo 📊 Monitor services:
echo    docker-compose ps
echo    docker-compose logs -f [service-name]
echo.
pause 