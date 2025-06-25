# 🚀 Complete ValMed Setup Guide - Poetry & Alembic Ready!

## ✅ Status: Dependencies Fixed, Configuration Required

Your Poetry and Alembic migration is **100% COMPLETE**! All dependency issues have been resolved. You now need to configure the environment variables to run the full application.

## 📋 Step 1: Create Environment Configuration

Create a file called `.env` in the `backend` directory with this content:

```bash
# backend/.env

# Database Configuration
DATABASE_URL=postgresql://valmed:valmedpass@db:5432/valmed

# For development with SQLite (uncomment to use instead of PostgreSQL):
# DATABASE_URL=sqlite:///./valmed.db

# Auth0 Configuration (Required for Auth0 integration)
AUTH0_DOMAIN=dev-example.us.auth0.com
AUTH0_CLIENT_ID=your-auth0-client-id
AUTH0_CLIENT_SECRET=your-auth0-client-secret
AUTH0_API_AUDIENCE=https://valmed-api.example.com

# Security
SECRET_KEY=dev-secret-key-change-in-production-make-it-long-and-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO

# API Configuration
API_KEY=dev-api-key-for-testing
```

## 🐳 Step 2: Run the Complete Application Stack

### Option A: Full Docker Compose (Recommended)

```bash
# 1. Go to project root
cd /path/to/ValMed

# 2. Build and start all services
docker-compose up --build

# 3. In another terminal, run database migrations
docker-compose run --rm migrations

# 4. Access your application:
# - Backend API: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
# - Frontend: http://medlog.local (if configured)
```

### Option B: Backend + Database Only

```bash
# Start just backend and database
docker-compose up db backend --build

# Run migrations
docker-compose run --rm migrations
```

### Option C: Development Mode (Local Poetry)

```bash
# 1. Go to backend directory
cd backend

# 2. Activate Poetry environment
.venv-new\Scripts\Activate.ps1

# 3. Run migrations
poetry run alembic upgrade head

# 4. Start development server
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔧 Step 3: Auth0 Configuration (For Production)

If you want to use real Auth0 authentication:

1. **Create Auth0 Account**: Go to https://auth0.com
2. **Create Application**: 
   - Type: Machine to Machine
   - Name: ValMed API
3. **Create API**:
   - Name: ValMed API
   - Identifier: `https://valmed-api.yourdomain.com`
4. **Update .env** with real values:
   ```
   AUTH0_DOMAIN=your-tenant.us.auth0.com
   AUTH0_API_AUDIENCE=https://valmed-api.yourdomain.com
   ```

## 🧪 Step 4: Test the Application

### Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### API Documentation
```bash
# Open in browser:
http://localhost:8000/docs
```

### Basic API Test
```bash
curl -H "X-API-Key: dev-api-key-for-testing" http://localhost:8000/api/drugs
```

## 📊 Step 5: Database Management

### Create New Migration
```bash
# After modifying models
poetry run alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations
```bash
poetry run alembic upgrade head
```

### Rollback Migration
```bash
poetry run alembic downgrade -1
```

### Check Migration Status
```bash
poetry run alembic current
poetry run alembic history
```

## 🗂️ Step 6: Development Workflow

### Daily Development
```bash
# 1. Start services
docker-compose up -d db

# 2. Activate Poetry environment
cd backend && .venv-new\Scripts\Activate.ps1

# 3. Run in development mode
poetry run uvicorn main:app --reload

# 4. Make changes to code
# 5. Create migrations if models changed
poetry run alembic revision --autogenerate -m "Your changes"

# 6. Apply migrations
poetry run alembic upgrade head
```

### Adding New Dependencies
```bash
# Add to pyproject.toml or use:
poetry add package-name

# For dev dependencies:
poetry add --group dev package-name

# Rebuild Docker after adding dependencies:
docker-compose build backend
```

## 🎯 Quick Start Commands

```bash
# Create the .env file first (see Step 1), then:

# Full stack startup:
docker-compose up --build

# Run migrations:
docker-compose run --rm migrations

# Test the API:
curl http://localhost:8000/health
```

## 🔍 Troubleshooting

### Common Issues:

1. **Auth0 Error**: Use development values in .env for testing
2. **Database Connection**: Ensure PostgreSQL is running via docker-compose
3. **Port Conflicts**: Change port in docker-compose.yml if 8000 is busy
4. **Migration Errors**: Check database connection and run `alembic current`

### Debug Commands:
```bash
# Check container logs
docker-compose logs backend

# Check database connection
docker-compose exec db psql -U valmed -d valmed

# Check Poetry environment
poetry show
poetry check
```

## 🎉 Success!

Your ValMed application now has:
- ✅ Professional Poetry dependency management
- ✅ Proper database migrations with Alembic
- ✅ Docker containerization
- ✅ Environment-based configuration
- ✅ Development and production workflows

The architectural transformation is complete! 🚀 