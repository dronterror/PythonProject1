"""
Redis cache integration for ValMed application.
Implements cache-aside pattern for improved performance on frequently accessed data.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from config import settings

logger = logging.getLogger(__name__)

class InMemoryCache:
    """In-memory cache fallback when Redis is unavailable."""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            if key in self._expiry and datetime.now() > self._expiry[key]:
                del self._cache[key]
                del self._expiry[key]
                return None
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, expire_seconds: int = 300) -> bool:
        self._cache[key] = value
        self._expiry[key] = datetime.now() + timedelta(seconds=expire_seconds)
        return True
    
    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            return True
        return False
    
    def flush_all(self) -> bool:
        self._cache.clear()
        self._expiry.clear()
        return True

class RedisCache:
    """Redis cache client with JSON serialization support."""
    
    def __init__(self):
        try:
            import redis
            # Use Docker service name for Redis connection
            self.redis_client = redis.Redis(
                host='redis',  # Docker service name
                port=6379,
                db=0,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.warning(f"Redis not available ({e}), using in-memory cache fallback")
            # Use in-memory fallback if Redis is unavailable
            self.redis_client = None
            self._fallback = InMemoryCache()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache and deserialize from JSON."""
        if not self.redis_client:
            return self._fallback.get(key)
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return None
    
    def set(self, key: str, value: Any, expire_seconds: int = 300) -> bool:
        """Set value in cache with JSON serialization and expiration."""
        if not self.redis_client:
            return self._fallback.set(key, value, expire_seconds)
        
        try:
            serialized_value = json.dumps(value, default=str)  # default=str handles UUID and datetime
            result = self.redis_client.setex(key, expire_seconds, serialized_value)
            return result
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis_client:
            return self._fallback.delete(key)
        
        try:
            result = self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE error for key '{key}': {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.redis_client:
            # Simple pattern matching for in-memory cache
            deleted = 0
            keys_to_delete = [k for k in self._fallback._cache.keys() if pattern.replace('*', '') in k]
            for key in keys_to_delete:
                if self._fallback.delete(key):
                    deleted += 1
            return deleted
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis DELETE PATTERN error for pattern '{pattern}': {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.redis_client:
            return key in self._fallback._cache
        
        try:
            return self.redis_client.exists(key)
        except Exception as e:
            logger.error(f"Redis EXISTS error for key '{key}': {e}")
            return False
    
    def flush_all(self) -> bool:
        """Clear all cache (use with caution)."""
        if not self.redis_client:
            return self._fallback.flush_all()
        
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis FLUSH error: {e}")
            return False


# Global cache instance
cache = RedisCache()

# Cache key constants
class CacheKeys:
    FORMULARY = "formulary:all"
    INVENTORY_STATUS = "inventory:status"
    LOW_STOCK_DRUGS = "drugs:low_stock"
    ACTIVE_ORDERS = "orders:active"
    USER_PERMISSIONS = "user:permissions:{user_id}"
    MAR_DASHBOARD = "mar:dashboard"

# Cache expiration times (in seconds)
class CacheExpiration:
    FORMULARY = 300  # 5 minutes - formulary doesn't change often
    INVENTORY_STATUS = 60  # 1 minute - stock levels change more frequently
    LOW_STOCK_DRUGS = 120  # 2 minutes
    ACTIVE_ORDERS = 30  # 30 seconds - orders are dynamic
    USER_PERMISSIONS = 900  # 15 minutes
    MAR_DASHBOARD = 60  # 1 minute


class CacheService:
    """High-level cache service with domain-specific methods."""
    
    @staticmethod
    def get_formulary() -> Optional[List[Dict[str, Any]]]:
        """Get cached formulary data."""
        return cache.get(CacheKeys.FORMULARY)
    
    @staticmethod
    def set_formulary(formulary_data: List[Dict[str, Any]]) -> bool:
        """Cache formulary data."""
        return cache.set(CacheKeys.FORMULARY, formulary_data, CacheExpiration.FORMULARY)
    
    @staticmethod
    def get_inventory_status() -> Optional[Dict[str, Dict[str, Any]]]:
        """Get cached inventory status."""
        return cache.get(CacheKeys.INVENTORY_STATUS)
    
    @staticmethod
    def set_inventory_status(inventory_data: Dict[str, Dict[str, Any]]) -> bool:
        """Cache inventory status."""
        return cache.set(CacheKeys.INVENTORY_STATUS, inventory_data, CacheExpiration.INVENTORY_STATUS)
    
    @staticmethod
    def get_low_stock_drugs() -> Optional[List[Dict[str, Any]]]:
        """Get cached low stock drugs."""
        return cache.get(CacheKeys.LOW_STOCK_DRUGS)
    
    @staticmethod
    def set_low_stock_drugs(low_stock_data: List[Dict[str, Any]]) -> bool:
        """Cache low stock drugs."""
        return cache.set(CacheKeys.LOW_STOCK_DRUGS, low_stock_data, CacheExpiration.LOW_STOCK_DRUGS)
    
    @staticmethod
    def get_mar_dashboard() -> Optional[Dict[str, Any]]:
        """Get cached MAR dashboard data."""
        return cache.get(CacheKeys.MAR_DASHBOARD)
    
    @staticmethod
    def set_mar_dashboard(dashboard_data: Dict[str, Any]) -> bool:
        """Cache MAR dashboard data."""
        return cache.set(CacheKeys.MAR_DASHBOARD, dashboard_data, CacheExpiration.MAR_DASHBOARD)
    
    @staticmethod
    def invalidate_drug_caches() -> None:
        """
        Invalidate all drug-related caches when drug data changes.
        Called after drug creation, updates, or stock changes.
        """
        cache.delete(CacheKeys.FORMULARY)
        cache.delete(CacheKeys.INVENTORY_STATUS)
        cache.delete(CacheKeys.LOW_STOCK_DRUGS)
        logger.info("Invalidated drug-related caches")
    
    @staticmethod
    def invalidate_order_caches() -> None:
        """
        Invalidate order-related caches when order data changes.
        Called after order creation, updates, or administrations.
        """
        cache.delete(CacheKeys.ACTIVE_ORDERS)
        cache.delete(CacheKeys.MAR_DASHBOARD)
        logger.info("Invalidated order-related caches")
    
    @staticmethod
    def invalidate_all_caches() -> None:
        """Invalidate all application caches."""
        cache.flush_all()
        logger.info("Invalidated all application caches") 