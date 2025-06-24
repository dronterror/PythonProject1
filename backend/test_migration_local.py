#!/usr/bin/env python3
"""
Local Test Migration Script for JWT Authentication
Simulates the Auth0 migration process for testing purposes
"""

import os
import sys
import secrets
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, UserRole

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestMigrationClient:
    """Simulates Auth0 migration for testing"""
    
    def __init__(self):
        self.created_users = []
        logger.info("Test Migration Client initialized")
    
    def create_user(self, email: str, password: str, role: str) -> str:
        """Simulate creating a user in Auth0"""
        # Generate a fake Auth0 user ID
        auth0_user_id = f"auth0|{secrets.token_hex(12)}"
        
        self.created_users.append({
            'email': email,
            'auth0_user_id': auth0_user_id,
            'role': role,
            'password': password
        })
        
        logger.info(f"Simulated Auth0 user creation: {email} -> {auth0_user_id}")
        return auth0_user_id

class TestUserMigrator:
    """Handles the user migration process"""
    
    def __init__(self):
        self.auth0_client = TestMigrationClient()
        self.migration_results = {
            'success': [],
            'failed': [],
            'total_processed': 0
        }
    
    def generate_temp_password(self) -> str:
        """Generate a secure temporary password"""
        return f"TempPass{secrets.token_urlsafe(8)}!"
    
    def migrate_user(self, db: Session, user: User) -> bool:
        """Migrate a single user to Auth0"""
        try:
            # Skip if already migrated
            if user.auth0_user_id:
                logger.info(f"User {user.email} already migrated (auth0_id: {user.auth0_user_id})")
                return True
            
            # Generate temporary password
            temp_password = self.generate_temp_password()
            
            # Create user in Auth0 (simulated)
            auth0_user_id = self.auth0_client.create_user(
                email=user.email,
                password=temp_password,
                role=user.role.value
            )
            
            # Update user in database
            user.auth0_user_id = auth0_user_id
            user.hashed_password = None  # Auth0 handles authentication now
            
            # Commit the change
            db.commit()
            
            self.migration_results['success'].append({
                'email': user.email,
                'auth0_user_id': auth0_user_id,
                'role': user.role.value,
                'temp_password': temp_password
            })
            
            logger.info(f"✓ Successfully migrated user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to migrate user {user.email}: {str(e)}")
            db.rollback()
            self.migration_results['failed'].append({
                'email': user.email,
                'error': str(e)
            })
            return False
    
    def migrate_all_users(self, db: Session) -> Dict[str, Any]:
        """Migrate all users to Auth0"""
        logger.info("Starting user migration to Auth0...")
        
        # Get all users
        users = db.query(User).all()
        total_users = len(users)
        
        logger.info(f"Found {total_users} users to migrate")
        
        # Migrate each user
        for i, user in enumerate(users, 1):
            logger.info(f"Migrating user {i}/{total_users}: {user.email}")
            self.migrate_user(db, user)
            self.migration_results['total_processed'] += 1
        
        # Generate migration report
        report = {
            'total_users': total_users,
            'successful_migrations': len(self.migration_results['success']),
            'failed_migrations': len(self.migration_results['failed']),
            'migration_results': self.migration_results
        }
        
        return report
    
    def print_migration_report(self, report: Dict[str, Any]):
        """Print a detailed migration report"""
        print("\n" + "="*60)
        print("MIGRATION REPORT")
        print("="*60)
        print(f"Total Users: {report['total_users']}")
        print(f"Successful Migrations: {report['successful_migrations']}")
        print(f"Failed Migrations: {report['failed_migrations']}")
        print(f"Success Rate: {(report['successful_migrations']/report['total_users']*100):.1f}%")
        
        if report['migration_results']['success']:
            print("\n✓ SUCCESSFUL MIGRATIONS:")
            for user in report['migration_results']['success']:
                print(f"  • {user['email']} ({user['role']}) -> {user['auth0_user_id']}")
                print(f"    Temp Password: {user['temp_password']}")
        
        if report['migration_results']['failed']:
            print("\n✗ FAILED MIGRATIONS:")
            for user in report['migration_results']['failed']:
                print(f"  • {user['email']}: {user['error']}")
        
        print("\n" + "="*60)

def main():
    """Main migration function"""
    print("🚀 Starting JWT Authentication Migration")
    print("This will migrate all users from API key to Auth0 JWT authentication")
    
    # Confirm migration
    confirm = input("\nProceed with migration? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Migration cancelled.")
        return
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Initialize migrator
        migrator = TestUserMigrator()
        
        # Run migration
        report = migrator.migrate_all_users(db)
        
        # Print report
        migrator.print_migration_report(report)
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        users = db.query(User).all()
        migrated_count = sum(1 for user in users if user.auth0_user_id is not None)
        print(f"Users with auth0_user_id: {migrated_count}/{len(users)}")
        
        if migrated_count == len(users):
            print("✅ Migration verification PASSED - All users migrated successfully!")
        else:
            print("⚠️  Migration verification FAILED - Some users not migrated")
            
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        db.rollback()
        print(f"\n❌ Migration failed: {str(e)}")
        
    finally:
        db.close()
    
    print("\n🎉 Migration process completed!")

if __name__ == "__main__":
    main() 