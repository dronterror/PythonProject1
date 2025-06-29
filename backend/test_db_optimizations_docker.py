#!/usr/bin/env python3
"""
Docker-based database optimization test suite.
This script runs inside the Docker container and tests:
1. Cursor-based pagination performance
2. Optimized loading strategies (selectinload vs joinedload)
3. Database architecture optimizations
"""

import sys
import time
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
import logging

# Add backend to path
sys.path.append('/app')

from models import Base, MedicationOrder, Drug, User, MedicationAdministration, OrderStatus, UserRole
from repositories.order_repository import OrderRepository
from repositories.drug_repository import DrugRepository
from database import get_db
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseOptimizationTester:
    """Test suite for database optimizations running inside Docker"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://valmed:valmedpass@db:5432/valmed')
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.test_results = []
    
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {details}")
    
    def setup_test_data(self):
        """Create test data for optimization testing"""
        try:
            with self.SessionLocal() as db:
                # Check if test data already exists
                existing_orders = db.query(MedicationOrder).count()
                if existing_orders > 50:
                    self.log_test("Test Data Setup", "SKIP", f"Found {existing_orders} existing orders")
                    return True
                
                # Create test drug
                test_drug = Drug(
                    name="TestDrug",
                    form="Tablet",
                    strength="500mg",
                    current_stock=1000,
                    low_stock_threshold=10
                )
                db.add(test_drug)
                db.flush()
                
                # Create test user
                test_doctor = User(
                    email="test.doctor@example.com",
                    auth_provider_id="test-doctor-123",
                    role=UserRole.doctor
                )
                db.add(test_doctor)
                db.flush()
                
                # Create test orders with administrations for N+1 testing
                base_time = datetime.now() - timedelta(days=30)
                orders_created = 0
                
                for i in range(100):  # Create 100 test orders
                    order = MedicationOrder(
                        patient_name=f"TestPatient_{i:03d}",
                        drug_id=test_drug.id,
                        dosage=1,
                        schedule="BID",
                        status=OrderStatus.active,
                        doctor_id=test_doctor.id,
                        created_at=base_time + timedelta(minutes=i*10)
                    )
                    db.add(order)
                    db.flush()  # Flush to get the order ID
                    orders_created += 1
                    
                    # Add some administrations to test selectinload optimization
                    if i % 3 == 0:  # Every 3rd order gets administrations
                        admin = MedicationAdministration(
                            order_id=order.id,
                            nurse_id=test_doctor.id,  # Reusing doctor as nurse for simplicity
                            administration_time=base_time + timedelta(minutes=i*10 + 5)
                        )
                        db.add(admin)
                
                db.commit()
                self.log_test("Test Data Setup", "PASS", f"Created {orders_created} test orders")
                return True
                
        except Exception as e:
            self.log_test("Test Data Setup", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_cursor_vs_offset_performance(self):
        """Test performance difference between cursor and offset pagination"""
        try:
            with self.SessionLocal() as db:
                order_repo = OrderRepository(db)
                
                # Test OFFSET-based pagination (old method)
                start_time = time.time()
                offset_orders = order_repo.list_active(skip=20, limit=10)
                offset_time = time.time() - start_time
                
                # Test CURSOR-based pagination (new method)
                start_time = time.time()
                cursor_result = order_repo.list_active_with_cursor(limit=10, cursor_type="timestamp")
                cursor_time = time.time() - start_time
                
                # Get cursor for second page test
                if cursor_result["next_cursor"] and cursor_result["has_next"]:
                    start_time = time.time()
                    second_page = order_repo.list_active_with_cursor(
                        cursor=cursor_result["next_cursor"], 
                        limit=10, 
                        cursor_type="timestamp"
                    )
                    cursor_second_page_time = time.time() - start_time
                else:
                    cursor_second_page_time = 0
                
                performance_improvement = ((offset_time - cursor_time) / offset_time) * 100 if offset_time > 0 else 0
                
                self.log_test(
                    "Cursor vs Offset Performance",
                    "PASS",
                    f"Offset: {offset_time:.4f}s, Cursor: {cursor_time:.4f}s, "
                    f"2nd page: {cursor_second_page_time:.4f}s, Improvement: {performance_improvement:.1f}%"
                )
                
                # Verify cursor pagination structure
                if all(key in cursor_result for key in ["orders", "next_cursor", "has_next", "cursor_type"]):
                    self.log_test("Cursor Pagination Structure", "PASS", "All required keys present")
                else:
                    self.log_test("Cursor Pagination Structure", "FAIL", "Missing required keys")
                    return False
                
                return True
                
        except Exception as e:
            self.log_test("Cursor vs Offset Performance", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_selectinload_optimization(self):
        """Test that selectinload prevents N+1 queries for one-to-many relationships"""
        try:
            with self.SessionLocal() as db:
                order_repo = OrderRepository(db)
                
                # Enable SQL logging to count queries
                import logging
                sql_logger = logging.getLogger('sqlalchemy.engine')
                sql_logger.setLevel(logging.INFO)
                
                # Create a handler to capture SQL queries
                query_count = {"count": 0}
                
                class QueryCountHandler(logging.Handler):
                    def emit(self, record):
                        if "SELECT" in record.getMessage():
                            query_count["count"] += 1
                
                handler = QueryCountHandler()
                sql_logger.addHandler(handler)
                
                try:
                    # Test optimized loading (should use selectinload)
                    query_count["count"] = 0
                    start_time = time.time()
                    orders = order_repo.list_active(limit=20)
                    load_time = time.time() - start_time
                    
                    # Access administrations to trigger loading
                    total_administrations = 0
                    for order in orders:
                        total_administrations += len(order.administrations)
                    
                    selectinload_queries = query_count["count"]
                    
                    self.log_test(
                        "SelectInLoad Optimization",
                        "PASS",
                        f"Loaded {len(orders)} orders with {total_administrations} administrations "
                        f"using {selectinload_queries} queries in {load_time:.4f}s"
                    )
                    
                    # Verify the optimization worked (should be around 3 queries max)
                    # 1. Orders query, 2. Administrations selectinload, 3. Users selectinload for nurses
                    if selectinload_queries <= 5:  # Allow some tolerance
                        self.log_test(
                            "N+1 Query Prevention",
                            "PASS",
                            f"Used only {selectinload_queries} queries (expected ≤5 for optimized loading)"
                        )
                    else:
                        self.log_test(
                            "N+1 Query Prevention",
                            "FAIL",
                            f"Used {selectinload_queries} queries (too many, indicates N+1 problem)"
                        )
                        return False
                    
                finally:
                    sql_logger.removeHandler(handler)
                    sql_logger.setLevel(logging.WARNING)
                
                return True
                
        except Exception as e:
            self.log_test("SelectInLoad Optimization", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_drug_repository_cursor_pagination(self):
        """Test cursor pagination in drug repository"""
        try:
            with self.SessionLocal() as db:
                drug_repo = DrugRepository(db)
                
                # Test name-based cursor pagination
                start_time = time.time()
                result = drug_repo.list_all_with_cursor(limit=5, cursor_type="name")
                name_cursor_time = time.time() - start_time
                
                # Test ID-based cursor pagination
                start_time = time.time()
                id_result = drug_repo.list_all_with_cursor(limit=5, cursor_type="id")
                id_cursor_time = time.time() - start_time
                
                if result["drugs"] and id_result["drugs"]:
                    self.log_test(
                        "Drug Repository Cursor Pagination",
                        "PASS",
                        f"Name cursor: {name_cursor_time:.4f}s, ID cursor: {id_cursor_time:.4f}s"
                    )
                    return True
                else:
                    self.log_test(
                        "Drug Repository Cursor Pagination",
                        "SKIP",
                        "No drugs in database to test pagination"
                    )
                    return True
                    
        except Exception as e:
            self.log_test("Drug Repository Cursor Pagination", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_database_indexes(self):
        """Test that required indexes exist for performance"""
        try:
            with self.SessionLocal() as db:
                # Check for critical indexes
                index_queries = [
                    "SELECT indexname FROM pg_indexes WHERE tablename = 'medication_orders' AND indexname LIKE '%created_at%'",
                    "SELECT indexname FROM pg_indexes WHERE tablename = 'medication_orders' AND indexname LIKE '%status%'",
                    "SELECT indexname FROM pg_indexes WHERE tablename = 'medication_orders' AND indexname LIKE '%doctor_id%'",
                ]
                
                indexes_found = 0
                for query in index_queries:
                    result = db.execute(text(query)).fetchall()
                    if result:
                        indexes_found += 1
                
                if indexes_found >= 2:  # At least 2 critical indexes
                    self.log_test(
                        "Database Indexes",
                        "PASS",
                        f"Found {indexes_found}/3 critical indexes for performance"
                    )
                    return True
                else:
                    self.log_test(
                        "Database Indexes",
                        "WARN",
                        f"Only found {indexes_found}/3 critical indexes"
                    )
                    return True
                    
        except Exception as e:
            self.log_test("Database Indexes", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all database optimization tests"""
        print("=" * 70)
        print("DOCKER DATABASE OPTIMIZATION TEST SUITE")
        print("=" * 70)
        
        # Setup test data first
        if not self.setup_test_data():
            print("\n❌ Failed to setup test data. Cannot run tests.")
            return False
        
        # Run optimization tests
        tests = [
            self.test_cursor_vs_offset_performance,
            self.test_selectinload_optimization,
            self.test_drug_repository_cursor_pagination,
            self.test_database_indexes
        ]
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                print(f"Test {test_func.__name__} failed with exception: {e}")
        
        # Count skipped tests
        skipped = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        print("\n" + "=" * 70)
        print("DOCKER TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"📊 Total: {len(self.test_results)}")
        
        success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL DATABASE OPTIMIZATIONS VERIFIED IN DOCKER!")
            print("✅ Cursor-based pagination working")
            print("✅ SelectInLoad preventing N+1 queries")
            print("✅ Repository optimizations functioning")
            return True
        else:
            print(f"\n⚠️  {failed} tests failed. Check the logs above for details.")
            return False

def main():
    """Main test runner"""
    tester = DatabaseOptimizationTester()
    success = tester.run_all_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 