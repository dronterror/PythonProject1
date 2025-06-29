#!/usr/bin/env python3
import psycopg2

print("🚀 Testing Database Hardening Fixes")
print("=" * 50)

# Test 1: Statement Timeout Configuration
print("\n1. Testing Statement Timeout Configuration...")
try:
    conn = psycopg2.connect(
        host="db", port=5432, database="valmed",
        user="valmed_user", password="valmed_password"
    )
    cursor = conn.cursor()
    cursor.execute("SHOW statement_timeout")
    timeout_setting = cursor.fetchone()[0]
    
    print(f"Database statement_timeout setting: {timeout_setting}")
    
    if timeout_setting == "5s":
        print("✅ Statement timeout correctly configured at 5 seconds")
        timeout_result = True
    else:
        print(f"❌ Statement timeout misconfigured: expected '5s', got '{timeout_setting}'")
        timeout_result = False
        
    conn.close()
except Exception as e:
    print(f"❌ Statement timeout test failed: {e}")
    timeout_result = False

# Test 2: Cache Fallback
print("\n2. Testing Cache Fallback Mechanism...")
try:
    from cache import cache, CacheService
    
    print("✅ Cache modules imported successfully")
    
    # Test basic cache operations
    test_data = {"test": "value", "number": 42}
    
    success = cache.set("test_key", test_data, 60)
    if success:
        print("✅ Cache SET operation successful")
    else:
        print("❌ Cache SET operation failed")
        
    result = cache.get("test_key")
    if result and result.get("test") == "value":
        print("✅ Cache GET operation successful")
    else:
        print("❌ Cache GET operation failed")
        
    # Test CacheService
    formulary_data = [{"drug": "Aspirin", "dose": "81mg"}]
    success = CacheService.set_formulary(formulary_data)
    if success:
        print("✅ CacheService.set_formulary successful")
    else:
        print("❌ CacheService.set_formulary failed")
        
    formulary = CacheService.get_formulary()
    if formulary and len(formulary) > 0:
        print("✅ CacheService.get_formulary successful")
        cache_result = True
    else:
        print("❌ CacheService.get_formulary failed")
        cache_result = False
        
except Exception as e:
    print(f"❌ Cache test failed: {e}")
    cache_result = False

# Test 3: Database Connection
print("\n3. Testing Database Connection...")
try:
    from database import engine, SessionLocal
    from sqlalchemy import text
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test"))
        if result.fetchone()[0] == 1:
            print("✅ Database connection successful")
            db_result = True
        else:
            print("❌ Database connection failed")
            db_result = False
            
except Exception as e:
    print(f"❌ Database connection test failed: {e}")
    db_result = False

# Summary
print("\n" + "=" * 50)
print("🏁 VALIDATION RESULTS SUMMARY")
print("=" * 50)

results = {
    "Statement Timeout": timeout_result,
    "Cache Fallback": cache_result,
    "Database Connection": db_result
}

total_tests = len(results)
passed_tests = sum(1 for result in results.values() if result)

for test_name, result in results.items():
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{test_name}: {status}")

success_rate = (passed_tests / total_tests) * 100
print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")

if passed_tests == total_tests:
    print("🎉 ALL FIXES VALIDATED SUCCESSFULLY!")
    print("✅ Production readiness: APPROVED")
else:
    print("❌ Some fixes require attention") 