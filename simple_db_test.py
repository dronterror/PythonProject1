#!/usr/bin/env python3
"""
Simple test to verify database optimizations
"""

import sys
import os

# Add backend to path
sys.path.append('/app')

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from repositories.order_repository import OrderRepository
    
    # Test database connection
    db_url = os.getenv('DATABASE_URL', 'postgresql://valmed:valmedpass@db:5432/valmed')
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    
    print("=" * 50)
    print("DATABASE OPTIMIZATION VERIFICATION")
    print("=" * 50)
    
    with SessionLocal() as db:
        order_repo = OrderRepository(db)
        
        # Test 1: Verify cursor pagination method exists and works
        try:
            result = order_repo.list_active_with_cursor(limit=5, cursor_type="timestamp")
            print("✅ PASS: Cursor-based pagination method exists")
            print(f"   - Returned keys: {list(result.keys())}")
            print(f"   - Orders count: {len(result.get('orders', []))}")
            print(f"   - Has next: {result.get('has_next', False)}")
            print(f"   - Cursor type: {result.get('cursor_type', 'unknown')}")
        except Exception as e:
            print(f"❌ FAIL: Cursor pagination error: {e}")
        
        # Test 2: Verify offset pagination still works
        try:
            orders = order_repo.list_active(skip=0, limit=5)
            print("✅ PASS: Offset-based pagination still works")
            print(f"   - Orders count: {len(orders)}")
        except Exception as e:
            print(f"❌ FAIL: Offset pagination error: {e}")
        
        # Test 3: Verify MAR dashboard works
        try:
            dashboard_data = order_repo.get_mar_dashboard_data()
            print("✅ PASS: MAR dashboard method works")
            print(f"   - Dashboard keys: {list(dashboard_data.keys())}")
            print(f"   - Patients count: {len(dashboard_data.get('patients', []))}")
        except Exception as e:
            print(f"❌ FAIL: MAR dashboard error: {e}")
    
    print("\n🎉 DATABASE OPTIMIZATIONS VERIFICATION COMPLETE")
    
except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    sys.exit(1) 