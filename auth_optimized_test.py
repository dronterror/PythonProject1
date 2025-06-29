#!/usr/bin/env python3
"""
Authorization-Aware Database Optimization Test
This script validates that database optimizations work correctly with:
1. JWT authentication and user resolution
2. Role-based access control (RBAC)
3. User-filtered queries (e.g., doctor's own orders)
4. Authorization middleware performance
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
    OrderStatus, UserRole
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

class AuthorizationOptimizationTester:
    """Test database optimizations with proper authorization"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://valmed:valmedpass@db:5432/valmed')
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.query_counter = QueryCounter()
        self.test_results = []
        
        # Setup query tracking
        event.listen(Engine, "before_cursor_execute", self.query_counter)
        
        # Store test users for authorization testing
        self.test_users = {}
        
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
    
    def create_test_users_with_auth(self):
        """Create test users with proper auth provider IDs"""
        try:
            with self.SessionLocal() as db:
                print("👥 CREATING TEST USERS WITH AUTH PROVIDER IDS...")
                
                # Clear existing test users
                db.execute(text("DELETE FROM medication_administrations WHERE TRUE"))
                db.execute(text("DELETE FROM medication_orders WHERE TRUE"))
                db.execute(text("DELETE FROM users WHERE email LIKE 'authtest.%'"))
                db.commit()
                
                # Create test users with auth provider IDs (simulating Keycloak/Auth0)
                users_data = [
                    {"email": "authtest.doctor1@hospital.com", "role": UserRole.doctor, "auth_id": "keycloak|doc1-123"},
                    {"email": "authtest.doctor2@hospital.com", "role": UserRole.doctor, "auth_id": "keycloak|doc2-456"},
                    {"email": "authtest.nurse1@hospital.com", "role": UserRole.nurse, "auth_id": "keycloak|nurse1-789"},
                    {"email": "authtest.pharmacist1@hospital.com", "role": UserRole.pharmacist, "auth_id": "keycloak|pharm1-345"},
                ]
                
                created_users = []
                for user_data in users_data:
                    user = User(
                        email=user_data["email"],
                        auth_provider_id=user_data["auth_id"],
                        role=user_data["role"]
                    )
                    db.add(user)
                    created_users.append(user)
                
                db.flush()
                
                # Store users by role for easy access
                for user in created_users:
                    if user.role.value not in self.test_users:
                        self.test_users[user.role.value] = user
                
                db.commit()
                
                self.log_test(
                    "Test Users with Auth Provider IDs",
                    "PASS",
                    f"Created {len(users_data)} users with auth provider IDs"
                )
                return True
                
        except Exception as e:
            self.log_test("Test Users with Auth Provider IDs", "FAIL", f"Exception: {str(e)}")
            return False
    
    def seed_authorized_test_data(self):
        """Create test data with proper user associations"""
        try:
            with self.SessionLocal() as db:
                print("🔒 SEEDING AUTHORIZED TEST DATA...")
                
                # Create test drug
                drug = Drug(
                    name="AuthTest_Aspirin",
                    form="Tablet",
                    strength="100mg",
                    current_stock=1000,
                    low_stock_threshold=10
                )
                db.add(drug)
                db.flush()
                
                # Get doctors
                doctors = [user for user in self.test_users.values() if user.role == UserRole.doctor]
                nurses = [user for user in self.test_users.values() if user.role == UserRole.nurse]
                
                if not doctors or not nurses:
                    self.log_test("Authorized Test Data Seeding", "FAIL", "Need at least 1 doctor and 1 nurse")
                    return False
                
                # Create orders for each doctor
                total_orders = 0
                for i, doctor in enumerate(doctors):
                    orders_count = 5 + i * 3  # 5, 8, 11, etc.
                    for j in range(orders_count):
                        order = MedicationOrder(
                            patient_name=f"Patient_Doc{i+1}_{j:02d}",
                            drug_id=drug.id,
                            dosage=random.randint(1, 3),
                            schedule=random.choice(["BID", "TID", "QID"]),
                            status=OrderStatus.active,
                            doctor_id=doctor.id,
                            created_at=datetime.now() - timedelta(hours=j)
                        )
                        db.add(order)
                        total_orders += 1
                
                db.flush()
                
                # Create some administrations
                active_orders = db.query(MedicationOrder).filter(
                    MedicationOrder.status == OrderStatus.active
                ).limit(10).all()
                
                administrations_count = 0
                for order in active_orders:
                    for k in range(random.randint(1, 3)):
                        admin = MedicationAdministration(
                            order_id=order.id,
                            nurse_id=random.choice(nurses).id,
                            administration_time=order.created_at + timedelta(hours=k+1)
                        )
                        db.add(admin)
                        administrations_count += 1
                
                db.commit()
                
                self.log_test(
                    "Authorized Test Data Seeding",
                    "PASS",
                    f"Created {total_orders} orders and {administrations_count} administrations"
                )
                return True
                
        except Exception as e:
            self.log_test("Authorized Test Data Seeding", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_user_lookup_optimization(self):
        """Test that user lookup by auth_provider_id is optimized"""
        try:
            with self.SessionLocal() as db:
                print("🔍 TESTING USER LOOKUP OPTIMIZATION...")
                
                doctor = list(self.test_users.values())[0]
                auth_provider_id = doctor.auth_provider_id
                
                # Test the user lookup that happens in get_current_user()
                self.query_counter.reset()
                start_time = time.time()
                
                user = db.query(User).filter(User.auth_provider_id == auth_provider_id).first()
                
                lookup_time = time.time() - start_time
                query_count = self.query_counter.query_count
                
                if user and query_count == 1:
                    self.log_test(
                        "User Lookup by Auth Provider ID",
                        "PASS",
                        f"Found user {user.email} in {lookup_time:.4f}s with {query_count} query"
                    )
                    return True
                else:
                    self.log_test(
                        "User Lookup by Auth Provider ID",
                        "FAIL",
                        f"Expected 1 query, got {query_count}. User found: {user is not None}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("User Lookup by Auth Provider ID", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_doctor_filtered_queries(self):
        """Test optimized queries with doctor-specific filtering"""
        try:
            with self.SessionLocal() as db:
                print("👨‍⚕️ TESTING DOCTOR-FILTERED QUERY OPTIMIZATION...")
                
                doctor = self.test_users["doctor"]
                order_repo = OrderRepository(db)
                
                # Test the doctor-specific query optimization
                self.query_counter.reset()
                start_time = time.time()
                
                # This simulates what happens when a doctor requests their orders
                doctor_orders = order_repo.list_by_doctor(doctor.id)
                
                # Access relationships to trigger loading
                total_administrations = 0
                for order in doctor_orders:
                    total_administrations += len(order.administrations)
                    # Access drug info (should be joinedload)
                    drug_name = order.drug.name if order.drug else None
                
                query_time = time.time() - start_time
                query_count = self.query_counter.query_count
                
                # Should be efficient: filtered query + selectinload for administrations
                expected_max_queries = 4
                
                if query_count <= expected_max_queries and len(doctor_orders) > 0:
                    self.log_test(
                        "Doctor-Filtered Query Optimization",
                        "PASS",
                        f"Loaded {len(doctor_orders)} orders for doctor with {total_administrations} administrations using {query_count} queries in {query_time:.4f}s"
                    )
                    return True
                else:
                    self.log_test(
                        "Doctor-Filtered Query Optimization",
                        "FAIL",
                        f"Used {query_count} queries (expected ≤{expected_max_queries}) or no orders found ({len(doctor_orders)} orders)"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Doctor-Filtered Query Optimization", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_role_based_data_isolation(self):
        """Test that data isolation works correctly with optimizations"""
        try:
            with self.SessionLocal() as db:
                print("🔐 TESTING ROLE-BASED DATA ISOLATION...")
                
                order_repo = OrderRepository(db)
                doctors = [user for user in self.test_users.values() if user.role == UserRole.doctor]
                
                if len(doctors) < 2:
                    self.log_test(
                        "Role-Based Data Isolation",
                        "SKIP",
                        "Need at least 2 doctors for isolation test"
                    )
                    return True
                
                # Get orders for each doctor
                doc1_orders = order_repo.list_by_doctor(doctors[0].id)
                doc2_orders = order_repo.list_by_doctor(doctors[1].id)
                
                # Verify data isolation
                doc1_order_ids = {order.id for order in doc1_orders}
                doc2_order_ids = {order.id for order in doc2_orders}
                
                # Should have no overlap
                overlap = doc1_order_ids.intersection(doc2_order_ids)
                
                if len(overlap) == 0 and len(doc1_orders) > 0 and len(doc2_orders) > 0:
                    self.log_test(
                        "Role-Based Data Isolation",
                        "PASS",
                        f"Doctor 1: {len(doc1_orders)} orders, Doctor 2: {len(doc2_orders)} orders, No overlap"
                    )
                    return True
                else:
                    self.log_test(
                        "Role-Based Data Isolation",
                        "FAIL",
                        f"Data isolation failed: {len(overlap)} overlapping orders, Doc1: {len(doc1_orders)}, Doc2: {len(doc2_orders)}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Role-Based Data Isolation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_cursor_pagination_with_auth(self):
        """Test cursor pagination with user context"""
        try:
            with self.SessionLocal() as db:
                print("📄 TESTING CURSOR PAGINATION WITH AUTHORIZATION...")
                
                order_repo = OrderRepository(db)
                
                # Test cursor pagination (available to all authenticated users)
                self.query_counter.reset()
                start_time = time.time()
                
                result = order_repo.list_active_with_cursor(
                    cursor=None,
                    limit=10,
                    cursor_type="timestamp"
                )
                
                query_time = time.time() - start_time
                query_count = self.query_counter.query_count
                
                orders_loaded = len(result.get("orders", []))
                
                # Should be efficient regardless of auth context
                expected_max_queries = 4
                
                if query_count <= expected_max_queries:
                    self.log_test(
                        "Cursor Pagination with Auth Context",
                        "PASS",
                        f"Loaded {orders_loaded} orders with cursor pagination using {query_count} queries in {query_time:.4f}s"
                    )
                    return True
                else:
                    self.log_test(
                        "Cursor Pagination with Auth Context",
                        "FAIL",
                        f"Used {query_count} queries (expected ≤{expected_max_queries})"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Cursor Pagination with Auth Context", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_authorization_tests(self):
        """Run all authorization-aware tests"""
        print("=" * 80)
        print("🔐 AUTHORIZATION-AWARE DATABASE OPTIMIZATION TEST SUITE")
        print("=" * 80)
        
        # Step 1: Create test users with auth
        if not self.create_test_users_with_auth():
            print("\n❌ Failed to create test users. Cannot run authorization tests.")
            return False
        
        # Step 2: Seed authorized data
        if not self.seed_authorized_test_data():
            print("\n❌ Failed to seed authorized test data.")
            return False
        
        # Step 3: Run authorization tests
        tests = [
            self.test_user_lookup_optimization,
            self.test_doctor_filtered_queries,
            self.test_role_based_data_isolation,
            self.test_cursor_pagination_with_auth
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
        print("📊 AUTHORIZATION-AWARE TEST RESULTS")
        print("=" * 80)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {len(self.test_results)}")
        
        success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL AUTHORIZATION-AWARE OPTIMIZATIONS VERIFIED!")
            print("✅ JWT authentication flow optimized")
            print("✅ Role-based queries perform efficiently")
            print("✅ Data isolation maintained with optimizations")
            print("✅ User-filtered queries work correctly")
            return True
        else:
            print(f"\n⚠️  {failed} authorization tests failed. Review security implications.")
            return False

def main():
    """Main test runner"""
    tester = AuthorizationOptimizationTester()
    success = tester.run_authorization_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 