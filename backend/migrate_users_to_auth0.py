#!/usr/bin/env python3
"""
MedLogistics User Migration Script
==================================

This script migrates existing users from the API key system to Auth0.
It performs the following operations:
1. Creates users in Auth0 using the Management API
2. Updates local database with Auth0 user IDs
3. Assigns appropriate roles in Auth0

CRITICAL: This script should be run only ONCE during the migration process.

Usage:
    python migrate_users_to_auth0.py [--dry-run] [--batch-size=10]

Requirements:
    - Auth0 Management API credentials configured
    - Database connection available
    - All users must have valid email addresses
"""

import os
import sys
import logging
import secrets
import argparse
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import User, UserRole
import crud

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('user_migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MigrationResult:
    """Result of a single user migration"""
    email: str
    success: bool
    auth0_user_id: Optional[str] = None
    error_message: Optional[str] = None
    local_user_id: Optional[str] = None

class Auth0MigrationClient:
    """Client for Auth0 Management API operations"""
    
    def __init__(self, domain: str, client_id: str, client_secret: str):
        self.domain = domain
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.base_url = f"https://{domain}/api/v2"
        
    def get_management_token(self) -> str:
        """Get access token for Auth0 Management API"""
        if self.access_token:
            return self.access_token
            
        url = f"https://{self.domain}/oauth/token"
        headers = {"Content-Type": "application/json"}
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": f"https://{self.domain}/api/v2/",
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            self.access_token = response.json()["access_token"]
            logger.info("Successfully obtained Auth0 Management API token")
            return self.access_token
        except requests.RequestException as e:
            logger.error(f"Failed to get Auth0 management token: {e}")
            raise
    
    def create_user(self, email: str, user_role: str) -> Dict[str, Any]:
        """Create a user in Auth0"""
        token = self.get_management_token()
        url = f"{self.base_url}/users"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Generate a secure temporary password
        temp_password = self._generate_temp_password()
        
        user_data = {
            "email": email,
            "password": temp_password,
            "connection": "Username-Password-Authentication",
            "email_verified": True,  # Skip email verification for migrated users
            "verify_email": False,   # Don't send welcome email during migration
            "app_metadata": {
                "roles": [user_role],
                "migrated": True,
                "migration_date": "2024-01-01"  # Update with actual date
            },
            "user_metadata": {
                "source": "api_key_migration"
            }
        }
        
        try:
            response = requests.post(url, json=user_data, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Created Auth0 user for {email}: {result['user_id']}")
            return result
        except requests.RequestException as e:
            logger.error(f"Failed to create Auth0 user for {email}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
    
    def assign_role_to_user(self, user_id: str, role_name: str) -> bool:
        """Assign a role to a user in Auth0 (if using Auth0 roles)"""
        # This is optional - roles can be managed via app_metadata
        # Implementation depends on your Auth0 role configuration
        logger.info(f"Role {role_name} assigned via app_metadata for user {user_id}")
        return True
    
    def _generate_temp_password(self) -> str:
        """Generate a secure temporary password"""
        # Generate a strong temporary password
        # Users will be forced to reset on first login
        password = secrets.token_urlsafe(16) + "Aa1!"
        return password

class UserMigrator:
    """Main migration orchestrator"""
    
    def __init__(self, auth0_client: Auth0MigrationClient, dry_run: bool = False):
        self.auth0_client = auth0_client
        self.dry_run = dry_run
        self.results: List[MigrationResult] = []
    
    def get_users_to_migrate(self, db: Session) -> List[User]:
        """Get all users that need to be migrated to Auth0"""
        try:
            # Find users without auth0_user_id
            users = db.query(User).filter(User.auth0_user_id.is_(None)).all()
            logger.info(f"Found {len(users)} users to migrate")
            return users
        except Exception as e:
            logger.error(f"Failed to fetch users from database: {e}")
            raise
    
    def migrate_user(self, db: Session, user: User) -> MigrationResult:
        """Migrate a single user to Auth0"""
        result = MigrationResult(email=user.email, success=False, local_user_id=str(user.id))
        
        try:
            logger.info(f"Starting migration for user: {user.email}")
            
            # Validate user data
            if not user.email or '@' not in user.email:
                raise ValueError(f"Invalid email address: {user.email}")
            
            if not user.role:
                raise ValueError(f"User {user.email} has no role assigned")
            
            # Create user in Auth0
            if not self.dry_run:
                auth0_user = self.auth0_client.create_user(
                    email=user.email,
                    user_role=user.role.value
                )
                auth0_user_id = auth0_user['user_id']
                result.auth0_user_id = auth0_user_id
                
                # Update local database with Auth0 ID
                user.auth0_user_id = auth0_user_id
                db.commit()
                
                logger.info(f"✓ Successfully migrated {user.email} -> {auth0_user_id}")
            else:
                logger.info(f"[DRY RUN] Would migrate {user.email} with role {user.role.value}")
                result.auth0_user_id = f"auth0|mock_{user.id}"
            
            result.success = True
            
        except Exception as e:
            db.rollback()  # Rollback any database changes
            error_msg = str(e)
            result.error_message = error_msg
            logger.error(f"✗ Failed to migrate {user.email}: {error_msg}")
        
        return result
    
    def migrate_all_users(self, batch_size: int = 10) -> Dict[str, Any]:
        """Migrate all users in batches"""
        db = SessionLocal()
        migration_summary = {
            "total_users": 0,
            "successful_migrations": 0,
            "failed_migrations": 0,
            "errors": []
        }
        
        try:
            users_to_migrate = self.get_users_to_migrate(db)
            migration_summary["total_users"] = len(users_to_migrate)
            
            if not users_to_migrate:
                logger.info("No users found that need migration")
                return migration_summary
            
            logger.info(f"Starting migration of {len(users_to_migrate)} users")
            
            # Process users in batches
            for i in range(0, len(users_to_migrate), batch_size):
                batch = users_to_migrate[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}: users {i+1}-{min(i+batch_size, len(users_to_migrate))}")
                
                for user in batch:
                    result = self.migrate_user(db, user)
                    self.results.append(result)
                    
                    if result.success:
                        migration_summary["successful_migrations"] += 1
                    else:
                        migration_summary["failed_migrations"] += 1
                        migration_summary["errors"].append({
                            "email": result.email,
                            "error": result.error_message
                        })
                
                # Small delay between batches to avoid rate limiting
                import time
                time.sleep(1)
            
        except Exception as e:
            logger.error(f"Critical error during migration: {e}")
            migration_summary["errors"].append({"critical_error": str(e)})
        finally:
            db.close()
        
        return migration_summary
    
    def generate_report(self, summary: Dict[str, Any]) -> str:
        """Generate a detailed migration report"""
        report = []
        report.append("=" * 50)
        report.append("USER MIGRATION REPORT")
        report.append("=" * 50)
        report.append(f"Total users processed: {summary['total_users']}")
        report.append(f"Successful migrations: {summary['successful_migrations']}")
        report.append(f"Failed migrations: {summary['failed_migrations']}")
        report.append(f"Success rate: {(summary['successful_migrations']/summary['total_users']*100):.1f}%" if summary['total_users'] > 0 else "N/A")
        report.append("")
        
        if summary['successful_migrations'] > 0:
            report.append("SUCCESSFUL MIGRATIONS:")
            report.append("-" * 20)
            for result in self.results:
                if result.success:
                    report.append(f"✓ {result.email} -> {result.auth0_user_id}")
            report.append("")
        
        if summary['failed_migrations'] > 0:
            report.append("FAILED MIGRATIONS:")
            report.append("-" * 20)
            for result in self.results:
                if not result.success:
                    report.append(f"✗ {result.email}: {result.error_message}")
            report.append("")
        
        report.append("NEXT STEPS:")
        report.append("-" * 20)
        if summary['failed_migrations'] > 0:
            report.append("1. Review failed migrations and resolve issues")
            report.append("2. Re-run migration for failed users")
        if summary['successful_migrations'] > 0:
            report.append("3. Test Auth0 login for migrated users")
            report.append("4. Send password reset instructions to users")
            report.append("5. Disable old API key authentication")
        
        return "\n".join(report)

def verify_environment() -> tuple:
    """Verify all required environment variables are present"""
    required_vars = [
        "AUTH0_DOMAIN",
        "AUTH0_MANAGEMENT_CLIENT_ID", 
        "AUTH0_MANAGEMENT_CLIENT_SECRET",
        "DATABASE_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    return (
        os.getenv("AUTH0_DOMAIN"),
        os.getenv("AUTH0_MANAGEMENT_CLIENT_ID"),
        os.getenv("AUTH0_MANAGEMENT_CLIENT_SECRET")
    )

def verify_database_connection() -> bool:
    """Verify database connection and schema"""
    try:
        db = SessionLocal()
        # Check if auth0_user_id column exists
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='auth0_user_id'"))
        if not result.fetchone():
            logger.error("Database schema not ready: auth0_user_id column not found")
            return False
        
        db.close()
        logger.info("Database connection and schema verified")
        return True
    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return False

def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(description="Migrate users from API key system to Auth0")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no actual changes)")
    parser.add_argument("--batch-size", type=int, default=10, help="Number of users to process in each batch")
    parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    # Verify environment
    auth0_domain, management_client_id, management_client_secret = verify_environment()
    
    # Verify database
    if not verify_database_connection():
        sys.exit(1)
    
    # Confirmation prompt
    if not args.dry_run and not args.confirm:
        print("\n" + "="*50)
        print("CRITICAL: USER MIGRATION TO AUTH0")
        print("="*50)
        print("This script will:")
        print("1. Create users in Auth0")
        print("2. Update local database with Auth0 user IDs")
        print("3. This operation CANNOT be easily reversed")
        print("\nIMPORTANT: Ensure you have:")
        print("- Backed up your database")
        print("- Tested in a staging environment")
        print("- Configured Auth0 production tenant")
        print("="*50)
        
        confirm = input("Type 'MIGRATE' to proceed: ")
        if confirm != "MIGRATE":
            print("Migration cancelled.")
            sys.exit(0)
    
    # Initialize clients
    auth0_client = Auth0MigrationClient(auth0_domain, management_client_id, management_client_secret)
    migrator = UserMigrator(auth0_client, dry_run=args.dry_run)
    
    # Run migration
    mode = "DRY RUN" if args.dry_run else "PRODUCTION"
    logger.info(f"Starting user migration in {mode} mode")
    
    summary = migrator.migrate_all_users(batch_size=args.batch_size)
    
    # Generate and display report
    report = migrator.generate_report(summary)
    print("\n" + report)
    
    # Save report to file
    report_file = f"migration_report_{'dry_run_' if args.dry_run else ''}{int(time.time())}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"Migration report saved to: {report_file}")
    
    # Exit with appropriate code
    if summary['failed_migrations'] > 0:
        logger.warning("Migration completed with errors. Review the report.")
        sys.exit(1)
    else:
        logger.info("Migration completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main() 