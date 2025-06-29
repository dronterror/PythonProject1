#!/usr/bin/env python3
"""
Docker-based validation script for database hardening fixes.
Tests both statement timeout configuration and Redis cache fallback.
"""

import asyncio
import json
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_statement_timeout_config():
    """Test that statement timeout is correctly configured at 5 seconds."""
    try:
        import psycopg2
        
        # Connect to database using Docker service name
        conn = psycopg2.connect(
            host="db",
            port=5432,
            database="valmed",
            user="valmed_user",
            password="valmed_password"
        )
        
        cursor = conn.cursor()
        
        # Check current statement timeout setting
        cursor.execute("SHOW statement_timeout")
        timeout_setting = cursor.fetchone()[0]
        
        logger.info(f"Database statement_timeout setting: {timeout_setting}")
        
        # Verify it's set to 5 seconds
        if timeout_setting == "5s":
            logger.info("✅ Statement timeout correctly configured at 5 seconds")
            return True
        else:
            logger.error(f"❌ Statement timeout misconfigured: expected '5s', got '{timeout_setting}'")
            return False
            
    except Exception as e:
        logger.error(f"❌ Statement timeout test failed: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def test_cache_fallback():
    """Test Redis cache fallback mechanism."""
    try:
        # Import cache modules
        from cache import cache, CacheService
        
        logger.info("✅ Cache modules imported successfully")
        
        # Test basic cache operations
        test_data = {
            'timestamp': datetime.now().isoformat(),
            'test_value': 'cache_validation',
            'nested': {'key': 'value', 'number': 42}
        }
        
        # Test cache set
        success = cache.set('validation_test', test_data, 300)
        if success:
            logger.info("✅ Cache SET operation successful")
        else:
            logger.error("❌ Cache SET operation failed")
            return False
        
        # Test cache get
        retrieved = cache.get('validation_test')
        if retrieved and retrieved.get('test_value') == 'cache_validation':
            logger.info(f"✅ Cache GET operation successful: {retrieved}")
        else:
            logger.error(f"❌ Cache GET operation failed: {retrieved}")
            return False
        
        # Test cache exists
        exists = cache.exists('validation_test')
        if exists:
            logger.info("✅ Cache EXISTS check successful")
        else:
            logger.error("❌ Cache EXISTS check failed")
            return False
        
        # Test CacheService high-level methods
        formulary_data = [
            {'drug': 'Aspirin', 'dose': '81mg', 'route': 'PO'},
            {'drug': 'Metformin', 'dose': '500mg', 'route': 'PO'}
        ]
        
        success = CacheService.set_formulary(formulary_data)
        if success:
            logger.info("✅ CacheService.set_formulary successful")
        else:
            logger.error("❌ CacheService.set_formulary failed")
            return False
        
        formulary = CacheService.get_formulary()
        if formulary and len(formulary) == 2:
            logger.info(f"✅ CacheService.get_formulary successful: {len(formulary)} items")
        else:
            logger.error(f"❌ CacheService.get_formulary failed: {formulary}")
            return False
        
        # Test cache invalidation
        CacheService.invalidate_drug_caches()
        formulary_after_invalidation = CacheService.get_formulary()
        if formulary_after_invalidation is None:
            logger.info("✅ Cache invalidation successful")
        else:
            logger.error(f"❌ Cache invalidation failed: {formulary_after_invalidation}")
            return False
        
        # Test cache deletion
        deleted = cache.delete('validation_test')
        if deleted:
            logger.info("✅ Cache DELETE operation successful")
        else:
            logger.error("❌ Cache DELETE operation failed")
            return False
        
        # Verify deletion
        result_after_delete = cache.get('validation_test')  
        if result_after_delete is None:
            logger.info("✅ Cache deletion verified")
        else:
            logger.error(f"❌ Cache still exists after deletion: {result_after_delete}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Cache fallback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection with hardened configuration."""
    try:
        from database import engine, SessionLocal
        from sqlalchemy import text
        
        logger.info("Testing database connection...")
        
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            if result.fetchone()[0] == 1:
                logger.info("✅ Database connection successful")
            else:
                logger.error("❌ Database connection test failed")
                return False
        
        # Test session creation
        with SessionLocal() as session:
            result = session.execute(text("SELECT version()")).fetchone()
            logger.info(f"✅ Database session test successful: PostgreSQL version detected")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    logger.info("🚀 Starting Database Hardening Fixes Validation")
    logger.info("=" * 60)
    
    results = {}
    
    # Test 1: Statement Timeout Configuration
    logger.info("\n1. Testing Statement Timeout Configuration...")
    results['statement_timeout'] = test_statement_timeout_config()
    
    # Test 2: Database Connection
    logger.info("\n2. Testing Database Connection...")
    results['database_connection'] = test_database_connection()
    
    # Test 3: Cache Fallback Mechanism
    logger.info("\n3. Testing Cache Fallback Mechanism...")
    results['cache_fallback'] = test_cache_fallback()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("🏁 VALIDATION RESULTS SUMMARY")
    logger.info("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    logger.info(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL FIXES VALIDATED SUCCESSFULLY!")
        logger.info("✅ Production readiness: APPROVED")
        return True
    else:
        logger.error("❌ Some fixes require attention before production deployment")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 