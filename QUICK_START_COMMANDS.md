# 🚀 Quick Start Commands - ValMed Full Flow

## ✅ Current Status
- Poetry & Alembic: **COMPLETE** ✅
- Dependencies: **RESOLVED** ✅
- Configuration: **READY** ✅

## 🎯 Complete Application Flow

### 1. Start the Full Stack
```bash
# From project root (ValMed/)
docker-compose up --build
```

### 2. Run Database Migrations (in new terminal)
```bash
# Create and apply initial database schema
docker-compose run --rm migrations
```

### 3. Test the Application
```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# API Documentation (open in browser)
http://localhost:8000/docs

# Test API endpoints
curl -H "X-API-Key: dev-api-key-for-testing" http://localhost:8000/api/drugs
```

## 🔧 Alternative: Backend Only Development

```bash
# 1. Start database only
docker-compose up -d db

# 2. Go to backend directory
cd backend

# 3. Activate Poetry environment
.venv-new\Scripts\Activate.ps1

# 4. Run migrations
poetry run alembic upgrade head

# 5. Start development server
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 Database Management Commands

```bash
# Create new migration after model changes
poetry run alembic revision --autogenerate -m "Description"

# Apply migrations
poetry run alembic upgrade head

# Check migration status
poetry run alembic current

# View migration history
poetry run alembic history
```

## 🧪 API Testing Examples

```bash
# Health endpoint
curl http://localhost:8000/health

# Get all drugs (with API key)
curl -H "X-API-Key: dev-api-key-for-testing" http://localhost:8000/api/drugs

# API Documentation
curl http://localhost:8000/docs

# OpenAPI spec
curl http://localhost:8000/openapi.json
```

## 🎉 You're Ready!

Your ValMed application now has:
- ✅ Professional Poetry dependency management
- ✅ Alembic database migrations
- ✅ Complete Docker setup
- ✅ Environment configuration
- ✅ API endpoints ready for testing

**The architecture transformation is COMPLETE!** 🚀 