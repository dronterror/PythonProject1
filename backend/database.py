import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///medlog.db")

# CRITICAL: Production-grade engine configuration with REPEATABLE READ isolation
# This isolation level is MANDATORY for inventory systems to prevent:
# 1. Non-repeatable reads during concurrent stock checks
# 2. Phantom reads that could cause stock inconsistencies  
# 3. Lost updates in concurrent order fulfillment scenarios
engine = create_engine(
    DATABASE_URL,
    # MANDATORY: Set transaction isolation to REPEATABLE READ
    # This prevents non-repeatable reads and ensures data consistency
    # in high-concurrency scenarios with concurrent order processing
    isolation_level="REPEATABLE_READ",
    
    # Production connection pooling - STRICT REQUIREMENTS
    poolclass=QueuePool,
    pool_size=20,        # Maintain exactly 20 persistent connections
    max_overflow=10,     # Allow max 10 additional connections under load
    pool_recycle=1800,   # Recycle connections every 30 minutes (prevents stale connections)
    
    # CRITICAL: pool_pre_ping validates connections before use by issuing SELECT 1
    # This prevents the application from attempting to use stale/dead connections
    # from the pool, which could happen during database restarts, network blips,
    # or connection timeouts. Without this, the application would fail with
    # connection errors instead of transparently reconnecting.
    pool_pre_ping=True,  
    
    pool_timeout=30,     # Maximum wait time for connection acquisition
    
    # Performance settings for production
    echo=False,          # NEVER enable SQL logging in production
    echo_pool=False,     # NEVER enable pool logging in production
    
    # Database-specific optimizations
    connect_args={
        "application_name": "valmed_backend",
        # statement_timeout is configured at Docker level (5 seconds)
        # keeping timezone setting for consistency
        "options": "-c timezone=utc"
    } if "postgresql" in DATABASE_URL else {}
)

# Session factory with strict settings for data integrity
SessionLocal = sessionmaker(
    autocommit=False,    # NEVER use autocommit in transactional systems
    autoflush=False,     # Manual control over when changes are flushed
    bind=engine,
    expire_on_commit=False  # Prevent lazy loading issues after commit
)

Base = declarative_base()

def get_db():
    """
    Database dependency for FastAPI.
    CRITICAL: Ensures proper session lifecycle management and cleanup.
    Any exception will trigger session rollback to maintain consistency.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 