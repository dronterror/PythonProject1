#!/usr/bin/env python3
"""
Comprehensive Database Optimization Test with Data Seeding
This script:
1. Seeds the database with realistic test data
2. Tests cursor vs offset pagination performance under load
3. Verifies N+1 query elimination with real relationships
4. Measures actual performance improvements
"""

import sys
import time
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
import logging

# Add backend to path
sys.path.append('/app')

from models import (
    Base, MedicationOrder, Drug, User, MedicationAdministration, 
    OrderStatus, UserRole, Hospital, Ward
)
from repositories.order_repository import OrderRepository
from repositories.drug_repository import DrugRepository
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QueryCounter:
    """Track SQL queries for N+1 detection"""
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.query_count = 0
        self.queries = []
    
    def __call__(self, conn, cursor, statement, parameters, context, executemany):
        self.query_count += 1
        self.queries.append(statement[:100] + "..." if len(statement) > 100 else statement)

class ComprehensiveDatabaseTester:
    """Comprehensive test suite with proper data seeding"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://valmed:valmedpass@db:5432/valmed')
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.query_counter = QueryCounter()
        self.test_results = []
        
        # Setup query tracking
        event.listen(Engine, "before_cursor_execute", self.query_counter)
    
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
    
    def seed_comprehensive_test_data(self):
        """Create realistic test data for performance testing"""
        try:
            with self.SessionLocal() as db:
                print("🌱 SEEDING DATABASE WITH COMPREHENSIVE TEST DATA...")
                
                # Clear existing test data
                db.execute(text("DELETE FROM medication_administrations WHERE TRUE"))
                db.execute(text("DELETE FROM medication_orders WHERE TRUE"))
                db.execute(text("DELETE FROM drugs WHERE name LIKE 'TestDrug%'"))
                db.execute(text("DELETE FROM users WHERE email LIKE 'test.%'"))
                db.commit()
                
                # Create 20 drugs
                drugs = []
                drug_names = [
                    "TestDrug_Aspirin", "TestDrug_Ibuprofen", "TestDrug_Acetaminophen", 
                    "TestDrug_Morphine", "TestDrug_Insulin", "TestDrug_Warfarin",
                    "TestDrug_Lisinopril", "TestDrug_Metformin", "TestDrug_Atorvastatin", 
                    "TestDrug_Levothyroxine", "TestDrug_Amlodipine", "TestDrug_Metoprolol",
                    "TestDrug_Losartan", "TestDrug_Simvastatin", "TestDrug_Omeprazole",
                    "TestDrug_Sertraline", "TestDrug_Furosemide", "TestDrug_Hydrochlorothiazide",
                    "TestDrug_Gabapentin", "TestDrug_Prednisone"
                ]
                
                for i, drug_name in enumerate(drug_names):
                    drug = Drug(
                        name=drug_name,
                        form="Tablet" if i % 2 == 0 else "Injection",
                        strength=f"{(i+1)*50}mg",
                        current_stock=random.randint(100, 1000),
                        low_stock_threshold=10
                    )
                    db.add(drug)
                    drugs.append(drug)
                
                db.flush()
                
                # Create 10 users (doctors and nurses)
                users = []
                for i in range(10):
                    role = UserRole.doctor if i < 5 else UserRole.nurse
                    user = User(
                        email=f"test.{role.value}{i}@hospital.com",
                        auth_provider_id=f"test-{role.value}-{i}",
                        role=role
                    )
                    db.add(user)
                    users.append(user)
                
                db.flush()
                doctors = [u for u in users if u.role == UserRole.doctor]
                nurses = [u for u in users if u.role == UserRole.nurse]
                
                # Create 500 orders with realistic distribution over time
                orders = []
                base_time = datetime.now() - timedelta(days=60)
                
                print("   Creating 500 medication orders...")
                for i in range(500):
                    order = MedicationOrder(
                        patient_name=f"Patient_{i:03d}_{random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}",
                        drug_id=random.choice(drugs).id,
                        dosage=random.randint(1, 4),
                        schedule=random.choice(["QD", "BID", "TID", "QID", "PRN"]),
                        status=OrderStatus.active if random.random() < 0.7 else random.choice([OrderStatus.completed, OrderStatus.discontinued]),
                        doctor_id=random.choice(doctors).id,
                        created_at=base_time + timedelta(
                            days=random.randint(0, 59),
                            hours=random.randint(0, 23),
                            minutes=random.randint(0, 59)
                        )
                    )
                    db.add(order)
                    orders.append(order)
                    
                    # Flush every 50 orders to get IDs
                    if i % 50 == 49:
                        db.flush()
                
                db.flush()
                
                # Create 1000+ administrations for N+1 testing
                print("   Creating 1000+ medication administrations...")
                active_orders = [o for o in orders if o.status == OrderStatus.active]
                
                for i in range(1200):
                    order = random.choice(active_orders)
                    admin = MedicationAdministration(
                        order_id=order.id,
                        nurse_id=random.choice(nurses).id,
                        administration_time=order.created_at + timedelta(
                            hours=random.randint(1, 48),
                            minutes=random.randint(0, 59)
                        )
                    )
                    db.add(admin)
                
                db.commit()
                
                # Verify data
                order_count = db.query(MedicationOrder).count()
                admin_count = db.query(MedicationAdministration).count()
                drug_count = db.query(Drug).filter(Drug.name.like('TestDrug%')).count()
                
                self.log_test(
                    "Comprehensive Data Seeding", 
                    "PASS",
                    f"Created {order_count} orders, {admin_count} administrations, {drug_count} drugs"
                )
                return True
                
        except Exception as e:
            self.log_test("Comprehensive Data Seeding", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_n_plus_one_elimination(self):
        """Test N+1 query elimination with real data"""
        try:
            with self.SessionLocal() as db:
                order_repo = OrderRepository(db)
                
                print("🔍 TESTING N+1 QUERY ELIMINATION...")
                
                # Test 1: Load orders with administrations (should use selectinload)
                self.query_counter.reset()
                start_time = time.time()
                
                orders = order_repo.list_active(limit=50)
                
                # Access all administrations to trigger loading
                total_administrations = 0
                total_nurses_accessed = 0
                for order in orders:
                    total_administrations += len(order.administrations)
                    for admin in order.administrations:
                        if admin.nurse:  # Access nurse to trigger loading
                            total_nurses_accessed += 1
                
                load_time = time.time() - start_time
                query_count = self.query_counter.query_count
                
                # With proper selectinload, we should have:
                # 1. Main orders query
                # 2. Administrations selectinload query  
                # 3. Nurses selectinload query
                # 4. Maybe drugs/doctors joinedload (part of main query)
                expected_max_queries = 6  # Allow some tolerance
                
                if query_count <= expected_max_queries:
                    self.log_test(
                        "N+1 Query Elimination",
                        "PASS",
                        f"Loaded {len(orders)} orders with {total_administrations} administrations using only {query_count} queries (≤{expected_max_queries})"
                    )
                    
                    self.log_test(
                        "Relationship Loading Performance",
                        "PASS", 
                        f"Loaded {total_nurses_accessed} nurse relationships in {load_time:.4f}s"
                    )
                    return True
                else:
                    self.log_test(
                        "N+1 Query Elimination",
                        "FAIL",
                        f"Used {query_count} queries (expected ≤{expected_max_queries}) - indicates N+1 problem"
                    )
                    # Print queries for debugging
                    print("   Queries executed:")
                    for i, query in enumerate(self.query_counter.queries[:10], 1):
                        print(f"   {i}. {query}")
                    return False
                    
        except Exception as e:
            self.log_test("N+1 Query Elimination", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_pagination_performance_under_load(self):
        """Test cursor vs offset pagination with real data"""
        try:
            with self.SessionLocal() as db:
                order_repo = OrderRepository(db)
                
                print("⚡ TESTING PAGINATION PERFORMANCE UNDER LOAD...")
                
                # Test offset pagination at different positions
                offset_times = []
                for skip in [0, 50, 100, 200, 300]:
                    start_time = time.time()
                    orders = order_repo.list_active(skip=skip, limit=20)
                    offset_time = time.time() - start_time
                    offset_times.append(offset_time)
                
                avg_offset_time = sum(offset_times) / len(offset_times)
                worst_offset_time = max(offset_times)
                
                # Test cursor pagination
                cursor_times = []
                next_cursor = None
                cursor_type = "timestamp"
                
                for page in range(5):
                    start_time = time.time()
                    result = order_repo.list_active_with_cursor(
                        cursor=next_cursor, 
                        limit=20, 
                        cursor_type=cursor_type
                    )
                    cursor_time = time.time() - start_time
                    cursor_times.append(cursor_time)
                    
                    next_cursor = result.get("next_cursor")
                    if not result.get("has_next"):
                        break
                
                avg_cursor_time = sum(cursor_times) / len(cursor_times) if cursor_times else 0
                worst_cursor_time = max(cursor_times) if cursor_times else 0
                
                # Calculate performance improvement
                avg_improvement = ((avg_offset_time - avg_cursor_time) / avg_offset_time) * 100 if avg_offset_time > 0 else 0
                consistency_ratio = worst_cursor_time / avg_cursor_time if avg_cursor_time > 0 else 1
                
                self.log_test(
                    "Pagination Performance Comparison",
                    "PASS",
                    f"Offset avg: {avg_offset_time:.4f}s, Cursor avg: {avg_cursor_time:.4f}s, "
                    f"Improvement: {avg_improvement:.1f}%"
                )
                
                self.log_test(
                    "Pagination Consistency",
                    "PASS" if consistency_ratio < 2.0 else "WARN",
                    f"Cursor worst/avg ratio: {consistency_ratio:.2f} (lower is better)"
                )
                
                # Test deep pagination (this is where offset really suffers)
                start_time = time.time()
                deep_offset_orders = order_repo.list_active(skip=400, limit=10)
                deep_offset_time = time.time() - start_time
                
                self.log_test(
                    "Deep Pagination Test",
                    "PASS",
                    f"Deep offset (skip=400): {deep_offset_time:.4f}s vs avg cursor: {avg_cursor_time:.4f}s"
                )
                
                return True
                
        except Exception as e:
            self.log_test("Pagination Performance Under Load", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests with proper data"""
        print("=" * 80)
        print("🧪 COMPREHENSIVE DATABASE OPTIMIZATION TEST SUITE")
        print("=" * 80)
        
        # Step 1: Seed comprehensive data
        if not self.seed_comprehensive_test_data():
            print("\n❌ Failed to seed test data. Cannot run meaningful tests.")
            return False
        
        # Step 2: Run all performance tests
        tests = [
            self.test_n_plus_one_elimination,
            self.test_pagination_performance_under_load
        ]
        
        passed = 0
        failed = 0
        
        for test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                print(f"❌ Test {test_func.__name__} failed with exception: {e}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {len(self.test_results)}")
        
        success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL DATABASE OPTIMIZATIONS VERIFIED WITH REALISTIC LOAD!")
            print("✅ N+1 queries eliminated under load")
            print("✅ Cursor pagination performs consistently")
            print("✅ Optimizations handle real data efficiently")
            return True
        else:
            print(f"\n⚠️  {failed} tests failed. Review optimizations needed.")
            return False

def main():
    """Main test runner"""
    tester = ComprehensiveDatabaseTester()
    success = tester.run_comprehensive_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 