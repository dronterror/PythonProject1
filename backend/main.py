from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from database import engine, Base, SessionLocal
from routers import drugs, orders, administrations, admin
from routers.users import router as users_router
from config import settings

logging.basicConfig(level=getattr(logging, settings.log_level.upper()))

# NOTE: Database schema is now managed by Alembic migrations
# Run: poetry run alembic upgrade head

app = FastAPI(
    title="Medication Logistics Platform with Keycloak",
    description="Professional medication logistics platform with Keycloak OIDC authentication and admin capabilities",
    version="3.0.0"
)

# Define the origins list as per the plan
origins = [
    "http://localhost",
    "https://localhost",
    "http://medlog.local",
    "https://medlog.local",
    "http://localhost:5173", # Local dev
]

# CORS: Configure for unified frontend and Keycloak
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Use the new origins list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(drugs.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(administrations.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Medication Logistics MVP Backend"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup():
    """Startup event."""
    logger = logging.getLogger(__name__)
    logger.info("Application started successfully")

@app.on_event("shutdown")
async def shutdown():
    """Shutdown event."""
    logger = logging.getLogger(__name__)
    logger.info("Application shutdown complete") 