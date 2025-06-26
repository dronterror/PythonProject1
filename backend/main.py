from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from database import engine, Base
from routers import drugs, orders, administrations, admin
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
    "https://admin.medlog.local",
    "https://doctor.medlog.local",
    "https://pharmacist.medlog.local",
    # Add your local development URLs if you ever run the frontend outside of Docker
    "http://localhost:5173",
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
app.include_router(drugs.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(administrations.router, prefix="/api")
app.include_router(admin.router, prefix="/api")  # Admin endpoints

@app.get("/")
async def root():
    return {"message": "Medication Logistics MVP Backend"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 