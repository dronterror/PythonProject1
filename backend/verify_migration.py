#!/usr/bin/env python3
"""
MedLogistics Migration Verification Script
==========================================

This script verifies that the user migration from API keys to Auth0 was successful.
It checks:
1. All users have auth0_user_id values
2. No duplicate auth0_user_id values exist
3. All users have valid email addresses
4. Database constraints are satisfied

Usage:
    python verify_migration.py
"""

import os
import sys
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import User, UserRole

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MigrationVerifier:
    """Verifies the migration was completed successfully"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.errors = []
        self.warnings = []
    
    def verify_all_users_have_auth0_id(self) -> bool:
        """Verify all users have auth0_user_id"""
        try:
            users_without_auth0_id = self.db.query(User).filter(
                User.auth0_user_id.is_(None)
            ).all()
            
            if users_without_auth0_id:
                self.errors.append(f"Found {len(users_without_auth0_id)} users without auth0_user_id:")
                for user in users_without_auth0_id:
                    self.errors.append(f"  - {user.email} (ID: {user.id})")
                return False
            
            logger.info("✓ All users have auth0_user_id")
            return True
            
        except Exception as e:
            self.errors.append(f"Failed to check auth0_user_id: {e}")
            return False
    
    def verify_no_duplicate_auth0_ids(self) -> bool:
        """Verify no duplicate auth0_user_id values"""
        try:
            result = self.db.execute(text("""
                SELECT auth0_user_id, COUNT(*) as count
                FROM users 
                WHERE auth0_user_id IS NOT NULL
                GROUP BY auth0_user_id 
                HAVING COUNT(*) > 1
            """))
            
            duplicates = result.fetchall()
            if duplicates:
                self.errors.append(f"Found {len(duplicates)} duplicate auth0_user_id values:")
                for dup in duplicates:
                    self.errors.append(f"  - {dup.auth0_user_id} appears {dup.count} times")
                return False
            
            logger.info("✓ No duplicate auth0_user_id values found")
            return True
            
        except Exception as e:
            self.errors.append(f"Failed to check for duplicates: {e}")
            return False
    
    def verify_valid_email_addresses(self) -> bool:
        """Verify all users have valid email addresses"""
        try:
            users_with_invalid_email = self.db.query(User).filter(
                ~User.email.contains('@')
            ).all()
            
            if users_with_invalid_email:
                self.errors.append(f"Found {len(users_with_invalid_email)} users with invalid email:")
                for user in users_with_invalid_email:
                    self.errors.append(f"  - {user.email} (ID: {user.id})")
                return False
            
            logger.info("✓ All users have valid email addresses")
            return True
            
        except Exception as e:
            self.errors.append(f"Failed to check email addresses: {e}")
            return False
    
    def verify_user_roles(self) -> bool:
        """Verify all users have valid roles"""
        try:
            users_without_role = self.db.query(User).filter(
                User.role.is_(None)
            ).all()
            
            if users_without_role:
                self.errors.append(f"Found {len(users_without_role)} users without roles:")
                for user in users_without_role:
                    self.errors.append(f"  - {user.email} (ID: {user.id})")
                return False
            
            logger.info("✓ All users have valid roles")
            return True
            
        except Exception as e:
            self.errors.append(f"Failed to check user roles: {e}")
            return False
    
    def verify_database_constraints(self) -> bool:
        """Verify database constraints are satisfied"""
        try:
            # Check unique constraint on auth0_user_id
            result = self.db.execute(text("""
                SELECT COUNT(DISTINCT auth0_user_id) as unique_count,
                       COUNT(auth0_user_id) as total_count
                FROM users 
                WHERE auth0_user_id IS NOT NULL
            """))
            
            row = result.fetchone()
            if row.unique_count != row.total_count:
                self.errors.append(f"Unique constraint violation: {row.unique_count} unique vs {row.total_count} total auth0_user_ids")
                return False
            
            # Check unique constraint on email
            result = self.db.execute(text("""
                SELECT COUNT(DISTINCT email) as unique_count,
                       COUNT(email) as total_count
                FROM users
            """))
            
            row = result.fetchone()
            if row.unique_count != row.total_count:
                self.errors.append(f"Email unique constraint violation: {row.unique_count} unique vs {row.total_count} total emails")
                return False
            
            logger.info("✓ Database constraints satisfied")
            return True
            
        except Exception as e:
            self.errors.append(f"Failed to check database constraints: {e}")
            return False
    
    def get_migration_statistics(self) -> Dict[str, Any]:
        """Get migration statistics"""
        try:
            # Total users
            total_users = self.db.query(User).count()
            
            # Users with auth0_user_id
            migrated_users = self.db.query(User).filter(
                User.auth0_user_id.is_not(None)
            ).count()
            
            # Users by role
            role_stats = {}
            for role in UserRole:
                count = self.db.query(User).filter(User.role == role).count()
                role_stats[role.value] = count
            
            # Auth0 ID patterns
            auth0_pattern_stats = self.db.execute(text("""
                SELECT 
                    CASE 
                        WHEN auth0_user_id LIKE 'auth0|%' THEN 'auth0'
                        WHEN auth0_user_id LIKE 'google-oauth2|%' THEN 'google'
                        WHEN auth0_user_id LIKE 'github|%' THEN 'github'
                        ELSE 'other'
                    END as provider,
                    COUNT(*) as count
                FROM users 
                WHERE auth0_user_id IS NOT NULL
                GROUP BY 
                    CASE 
                        WHEN auth0_user_id LIKE 'auth0|%' THEN 'auth0'
                        WHEN auth0_user_id LIKE 'google-oauth2|%' THEN 'google'
                        WHEN auth0_user_id LIKE 'github|%' THEN 'github'
                        ELSE 'other'
                    END
            """)).fetchall()
            
            provider_stats = {row.provider: row.count for row in auth0_pattern_stats}
            
            return {
                "total_users": total_users,
                "migrated_users": migrated_users,
                "migration_rate": (migrated_users / total_users * 100) if total_users > 0 else 0,
                "role_distribution": role_stats,
                "provider_distribution": provider_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def run_all_verifications(self) -> bool:
        """Run all verification checks"""
        logger.info("Starting migration verification...")
        
        checks = [
            ("Users have Auth0 IDs", self.verify_all_users_have_auth0_id),
            ("No duplicate Auth0 IDs", self.verify_no_duplicate_auth0_ids),
            ("Valid email addresses", self.verify_valid_email_addresses),
            ("Valid user roles", self.verify_user_roles),
            ("Database constraints", self.verify_database_constraints)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            logger.info(f"Running check: {check_name}")
            if not check_func():
                all_passed = False
        
        return all_passed
    
    def generate_report(self, include_stats: bool = True) -> str:
        """Generate verification report"""
        report = []
        report.append("=" * 60)
        report.append("MIGRATION VERIFICATION REPORT")
        report.append("=" * 60)
        
        if include_stats:
            stats = self.get_migration_statistics()
            if stats:
                report.append("MIGRATION STATISTICS:")
                report.append("-" * 30)
                report.append(f"Total users: {stats.get('total_users', 'N/A')}")
                report.append(f"Migrated users: {stats.get('migrated_users', 'N/A')}")
                report.append(f"Migration rate: {stats.get('migration_rate', 0):.1f}%")
                report.append("")
                
                report.append("Role Distribution:")
                for role, count in stats.get('role_distribution', {}).items():
                    report.append(f"  - {role}: {count}")
                report.append("")
                
                report.append("Provider Distribution:")
                for provider, count in stats.get('provider_distribution', {}).items():
                    report.append(f"  - {provider}: {count}")
                report.append("")
        
        if not self.errors and not self.warnings:
            report.append("✓ VERIFICATION PASSED")
            report.append("All checks completed successfully!")
        else:
            report.append("✗ VERIFICATION FAILED")
            report.append("")
            
            if self.errors:
                report.append("ERRORS:")
                report.append("-" * 10)
                for error in self.errors:
                    report.append(f"✗ {error}")
                report.append("")
            
            if self.warnings:
                report.append("WARNINGS:")
                report.append("-" * 10)
                for warning in self.warnings:
                    report.append(f"⚠ {warning}")
                report.append("")
        
        report.append("NEXT STEPS:")
        report.append("-" * 15)
        if self.errors:
            report.append("1. Fix the errors listed above")
            report.append("2. Re-run the migration for failed users")
            report.append("3. Re-run this verification script")
        else:
            report.append("1. Test Auth0 login for sample users")
            report.append("2. Notify users about the new authentication system")
            report.append("3. Monitor authentication logs")
            report.append("4. Consider disabling old API key endpoints")
        
        return "\n".join(report)
    
    def cleanup(self):
        """Clean up database connection"""
        if self.db:
            self.db.close()

def main():
    """Main verification function"""
    verifier = MigrationVerifier()
    
    try:
        # Run all verifications
        success = verifier.run_all_verifications()
        
        # Generate and display report
        report = verifier.generate_report()
        print("\n" + report)
        
        # Save report to file
        import time
        report_file = f"verification_report_{int(time.time())}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Verification report saved to: {report_file}")
        
        # Exit with appropriate code
        if success:
            logger.info("✓ Migration verification completed successfully!")
            sys.exit(0)
        else:
            logger.error("✗ Migration verification failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Verification failed with critical error: {e}")
        sys.exit(1)
    finally:
        verifier.cleanup()

if __name__ == "__main__":
    main() 