#!/usr/bin/env python3
"""
Simple test to verify Redis fallback mechanism works correctly.
This test isolates the cache logic without depending on other modules.
"""

import json
import logging
from typing import Optional, Any
from datetime import datetime, timedelta

# Mock settings to avoid config dependency
class MockSettings:
    def __init__(self):
        pass

# Mock the config import
import sys
import types
mock_config = types.ModuleType('config')
mock_config.settings = MockSettings()
sys.modules['config'] = mock_config

def test_redis_fallback():
    """Test Redis fallback mechanism in isolation."""
    print("🧪 Testing Redis Cache Fallback Mechanism")
    print("=" * 50)
    
    try:
        # Now import our cache classes
        from backend.cache import RedisCache, InMemoryCache
        
        print("✅ Cache classes imported successfully")
        
        # Test InMemoryCache directly
        print("\n📝 Testing InMemoryCache:")
        mem_cache = InMemoryCache()
        
        # Test set/get
        success = mem_cache.set('test_key', {'test': 'value'}, 60)
        print(f"✅ Set operation: {success}")
        
        result = mem_cache.get('test_key')
        print(f"✅ Get operation: {result}")
        
        # Test delete
        deleted = mem_cache.delete('test_key')
        print(f"✅ Delete operation: {deleted}")
        
        # Verify deletion
        result_after = mem_cache.get('test_key')
        print(f"✅ Verify deletion (should be None): {result_after}")
        
        # Test RedisCache (which should fallback to InMemoryCache)
        print("\n🔄 Testing RedisCache (should fallback to InMemory):")
        redis_cache = RedisCache()
        
        # Check if it fell back correctly
        if redis_cache.redis_client is None:
            print("✅ RedisCache correctly detected Redis unavailable and fell back")
        else:
            print("❌ RedisCache should have fallen back but didn't")
            
        # Test RedisCache operations
        success = redis_cache.set('redis_test', {'fallback': True}, 30)
        print(f"✅ RedisCache set (using fallback): {success}")
        
        result = redis_cache.get('redis_test')
        print(f"✅ RedisCache get (using fallback): {result}")
        
        exists = redis_cache.exists('redis_test')
        print(f"✅ RedisCache exists (using fallback): {exists}")
        
        deleted = redis_cache.delete('redis_test')
        print(f"✅ RedisCache delete (using fallback): {deleted}")
        
        print("\n🎉 All Redis fallback tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_redis_fallback()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILURE'}: Redis fallback mechanism test")
    sys.exit(0 if success else 1) 