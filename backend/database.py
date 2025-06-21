import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///medlog.db")

# Optimized engine configuration with connection pooling
engine = create_engine(
    DATABASE_URL,
    # Connection pooling settings
    poolclass=QueuePool,
    pool_size=20,  # Number of connections to maintain
    max_overflow=30,  # Additional connections that can be created
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Timeout for getting connection from pool
    
    # Performance settings
    echo=False,  # Disable SQL logging in production
    echo_pool=False,  # Disable pool logging
    
    # PostgreSQL specific optimizations (if using PostgreSQL)
    connect_args={
        "application_name": "valmed_backend",
        "options": "-c timezone=utc -c statement_timeout=30000"  # 30 second timeout
    } if "postgresql" in DATABASE_URL else {}
)

# Optimized session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Prevent lazy loading issues
)

Base = declarative_base() 