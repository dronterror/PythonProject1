#!/usr/bin/env python3
"""
Pre-Migration Test Data Seeder
===============================

This script creates test users in the database WITHOUT auth0_user_id values.
This simulates the state before migration and is used for testing the migration process.

Usage:
    python seed_pre_migration_users.py [--count=5]
"""

import os
import sys
import logging
import argparse
import secrets
from sqlalchemy.orm import Session

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from models import User, UserRole, Base
from passlib.context import CryptContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_users(db: Session, count: int = 5) -> list:
    """Create test users for migration testing"""
    
    test_users_data = [
        {
            "email": "admin@test.medlog.app",
            "full_name": "System Administrator",
            "role": UserRole.super_admin,
            "is_active": True
        },
        {
            "email": "pharmacist1@test.medlog.app", 
            "full_name": "Alice Pharmacist",
            "role": UserRole.pharmacist,
            "is_active": True
        },
        {
            "email": "doctor1@test.medlog.app",
            "full_name": "Dr. Bob Johnson",
            "role": UserRole.doctor,
            "is_active": True
        },
        {
            "email": "nurse1@test.medlog.app",
            "full_name": "Carol Nurse",
            "role": UserRole.nurse,
            "is_active": True
        },
        {
            "email": "doctor2@test.medlog.app",
            "full_name": "Dr. David Smith",
            "role": UserRole.doctor,
            "is_active": True
        },
        {
            "email": "nurse2@test.medlog.app",
            "full_name": "Eva Martinez",
            "role": UserRole.nurse,
            "is_active": True
        },
        {
            "email": "pharmacist2@test.medlog.app",
            "full_name": "Frank Wilson",
            "role": UserRole.pharmacist,
            "is_active": True
        },
        {
            "email": "inactive@test.medlog.app",
            "full_name": "Inactive User",
            "role": UserRole.nurse,
            "is_active": False
        }
    ]
    
    created_users = []
    
    try:
        # Limit to requested count
        users_to_create = test_users_data[:count]
        
        for user_data in users_to_create:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if existing_user:
                logger.warning(f"User {user_data['email']} already exists, skipping")
                continue
            
            # Create user with hashed password and API key (old system)
            temp_password = "TempPassword123!"  # Users will reset this
            hashed_password = pwd_context.hash(temp_password)
            api_key = f"test_api_key_{secrets.token_urlsafe(16)}"
            
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=hashed_password,
                role=user_data["role"],
                is_active=user_data["is_active"],
                api_key=api_key,  # This is the old system field
                auth0_user_id=None  # This is None to simulate pre-migration state
            )
            
            db.add(user)
            created_users.append(user)
            logger.info(f"Created test user: {user_data['email']} (Role: {user_data['role'].value})")
        
        # Commit all users
        db.commit()
        logger.info(f"Successfully created {len(created_users)} test users")
        
        return created_users
        
    except Exception as e:
        logger.error(f"Failed to create test users: {e}")
        db.rollback()
        raise

def verify_pre_migration_state(db: Session) -> bool:
    """Verify the database is in the correct pre-migration state"""
    try:
        # Count users without auth0_user_id
        users_without_auth0 = db.query(User).filter(User.auth0_user_id.is_(None)).count()
        total_users = db.query(User).count()
        
        logger.info(f"Total users: {total_users}")
        logger.info(f"Users without auth0_user_id: {users_without_auth0}")
        
        if users_without_auth0 == 0:
            logger.warning("No users found without auth0_user_id - migration may have already run")
            return False
        
        # Check that users have the old API key field populated
        users_with_api_key = db.query(User).filter(User.api_key.is_not(None)).count()
        logger.info(f"Users with API keys: {users_with_api_key}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to verify pre-migration state: {e}")
        return False

def clear_existing_users(db: Session) -> None:
    """Clear existing users (for clean testing)"""
    try:
        user_count = db.query(User).count()
        if user_count > 0:
            logger.info(f"Clearing {user_count} existing users...")
            db.query(User).delete()
            db.commit()
            logger.info("Existing users cleared")
        else:
            logger.info("No existing users to clear")
    except Exception as e:
        logger.error(f"Failed to clear users: {e}")
        db.rollback()
        raise

def main():
    """Main seeding function"""
    parser = argparse.ArgumentParser(description="Seed database with pre-migration test users")
    parser.add_argument("--count", type=int, default=5, help="Number of test users to create")
    parser.add_argument("--clear", action="store_true", help="Clear existing users first")
    parser.add_argument("--verify-only", action="store_true", help="Only verify pre-migration state")
    
    args = parser.parse_args()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        if args.verify_only:
            logger.info("Verifying pre-migration state only...")
            if verify_pre_migration_state(db):
                logger.info("✓ Database is in correct pre-migration state")
            else:
                logger.warning("⚠ Database may not be in expected pre-migration state")
            return
        
        # Clear existing users if requested
        if args.clear:
            clear_existing_users(db)
        
        # Create test users
        logger.info(f"Creating {args.count} test users...")
        created_users = create_test_users(db, args.count)
        
        if created_users:
            # Verify state after creation
            if verify_pre_migration_state(db):
                logger.info("✓ Test data seeded successfully - ready for migration testing")
                
                # Display created users summary
                print("\n" + "="*50)
                print("TEST USERS CREATED")
                print("="*50)
                for user in created_users:
                    print(f"Email: {user.email}")
                    print(f"Role: {user.role.value}")
                    print(f"Active: {user.is_active}")
                    print(f"API Key: {user.api_key[:20]}...")
                    print(f"Auth0 ID: {user.auth0_user_id or 'None (pre-migration)'}")
                    print("-" * 30)
                
                print("Next steps:")
                print("1. Run database schema migration: alembic upgrade head")
                print("2. Run user migration: python migrate_users_to_auth0.py --dry-run")
                print("3. Verify migration: python verify_migration.py")
            else:
                logger.error("✗ Database not in expected state after seeding")
        else:
            logger.warning("No users were created")
    
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        sys.exit(1)
    
    finally:
        db.close()

if __name__ == "__main__":
    main() 