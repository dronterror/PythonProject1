from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from database import engine, Base
from routers import drugs, orders, administrations

logging.basicConfig(level=logging.INFO)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Medication Logistics MVP Backend",
    description="MVP backend for medication logistics platform",
    version="1.0.0"
)

# CORS: Restrict in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(drugs.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(administrations.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Medication Logistics MVP Backend"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 