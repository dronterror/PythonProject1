from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from database import engine, Base
from routers import drugs, orders, administrations, admin

logging.basicConfig(level=logging.INFO)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Medication Logistics Platform with Auth0",
    description="Professional medication logistics platform with Auth0 authentication and admin capabilities",
    version="2.0.0"
)

# CORS: Configure for multiple frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Admin frontend
        "http://localhost:5173",  # Original frontend  
        "http://localhost:4173",  # Production frontend
        # Add your production domains here
    ],
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