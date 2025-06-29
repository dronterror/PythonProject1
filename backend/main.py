from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from sqlalchemy.exc import OperationalError
from psycopg2.errors import QueryCanceled
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

@app.exception_handler(OperationalError)
async def query_timeout_handler(request: Request, exc: OperationalError):
    """
    Handle database query timeouts (statement_timeout violations).
    
    When a query exceeds the statement_timeout configured in PostgreSQL (5 seconds),
    PostgreSQL cancels the query and raises a QueryCanceled error, which SQLAlchemy
    wraps in an OperationalError. This handler ensures the application gracefully
    responds with a proper HTTP status instead of exposing internal error details.
    
    Returns 503 Service Unavailable to indicate the service is temporarily unable
    to handle the request due to database performance issues.
    """
    # Check if this is specifically a query cancellation
    if isinstance(exc.orig, QueryCanceled):
        logger = logging.getLogger(__name__)
        logger.warning(f"Query timeout exceeded on {request.url.path}: {str(exc.orig)}")
        
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service Temporarily Unavailable",
                "message": "Database query timeout - the request took too long to process",
                "detail": "Please try again with a more specific query or contact support if this persists",
                "type": "query_timeout"
            }
        )
    
    # Re-raise if it's not a query cancellation
    raise exc

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