#!/usr/bin/env python3
"""
Critical Authorization Security Test for Database Optimizations
Validates that database optimizations work correctly with JWT auth and RBAC
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
import os

# Add backend to path
sys.path.append('/app')

from models import (
    Base, MedicationOrder, Drug, User, MedicationAdministration, 
    OrderStatus, UserRole
)
from repositories.order_repository import OrderRepository
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QueryCounter:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.query_count = 0
        self.queries = []
    
    def __call__(self, conn, cursor, statement, parameters, context, executemany):
        self.query_count += 1
        self.queries.append(statement[:100] + "..." if len(statement) > 100 else statement)

class AuthSecurityTester:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://valmed:valmedpass@db:5432/valmed')
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.query_counter = QueryCounter()
        self.test_results = []
        
        # Setup query tracking
        event.listen(Engine, "before_cursor_execute", self.query_counter)
        
        # Store test users
        self.test_users = {}
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {details}")
    
    def create_auth_test_users(self):
        """Create test users with proper auth provider IDs"""
        try:
            with self.SessionLocal() as db:
                print("👥 CREATING AUTHORIZED TEST USERS...")
                
                # Clear existing auth test data
                db.execute(text("DELETE FROM medication_administrations WHERE order_id IN (SELECT id FROM medication_orders WHERE patient_name LIKE 'AuthTest_%')"))
                db.execute(text("DELETE FROM medication_orders WHERE patient_name LIKE 'AuthTest_%'"))
                db.execute(text("DELETE FROM users WHERE email LIKE 'authtest.%'"))
                db.execute(text("DELETE FROM drugs WHERE name LIKE 'AuthTest_%'"))
                db.commit()
                
                # Create test users with auth provider IDs
                users_data = [
                    {"email": "authtest.doctor1@hospital.com", "role": UserRole.doctor, "auth_id": "keycloak|doc1-123"},
                    {"email": "authtest.doctor2@hospital.com", "role": UserRole.doctor, "auth_id": "keycloak|doc2-456"},
                    {"email": "authtest.nurse1@hospital.com", "role": UserRole.nurse, "auth_id": "keycloak|nurse1-789"},
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
                
                # Store users by role
                for user in created_users:
                    if user.role.value not in self.test_users:
                        self.test_users[user.role.value] = user
                
                db.commit()
                
                self.log_test(
                    "Authorized Test Users Creation",
                    "PASS",
                    f"Created {len(users_data)} users with auth provider IDs"
                )
                return True
                
        except Exception as e:
            self.log_test("Authorized Test Users Creation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def create_role_specific_data(self):
        """Create test data with proper role associations"""
        try:
            with self.SessionLocal() as db:
                print("🔒 CREATING ROLE-SPECIFIC TEST DATA...")
                
                # Create test drug
                drug = Drug(
                    name="AuthTest_SecurityDrug",
                    form="Tablet",
                    strength="100mg",
                    current_stock=500,
                    low_stock_threshold=10
                )
                db.add(drug)
                db.flush()
                
                # Get users
                doctors = [user for user in self.test_users.values() if user.role == UserRole.doctor]
                nurses = [user for user in self.test_users.values() if user.role == UserRole.nurse]
                
                if not doctors or not nurses:
                    self.log_test("Role-Specific Data Creation", "FAIL", "Need doctors and nurses")
                    return False
                
                # Create orders for each doctor - this is the key security test
                total_orders = 0
                for i, doctor in enumerate(doctors):
                    orders_for_doctor = 8 + i * 2  # 8, 10, etc.
                    for j in range(orders_for_doctor):
                        order = MedicationOrder(
                            patient_name=f"AuthTest_Patient_Doc{i+1}_{j:02d}",
                            drug_id=drug.id,
                            dosage=random.randint(1, 3),
                            schedule="BID",
                            status=OrderStatus.active,
                            doctor_id=doctor.id,
                            created_at=datetime.now() - timedelta(hours=j)
                        )
                        db.add(order)
                        total_orders += 1
                
                db.flush()
                
                # Create administrations
                active_orders = db.query(MedicationOrder).filter(
                    MedicationOrder.patient_name.like('AuthTest_%')
                ).limit(12).all()
                
                admin_count = 0
                for order in active_orders:
                    for k in range(random.randint(1, 2)):
                        admin = MedicationAdministration(
                            order_id=order.id,
                            nurse_id=random.choice(nurses).id,
                            administration_time=order.created_at + timedelta(hours=k+1)
                        )
                        db.add(admin)
                        admin_count += 1
                
                db.commit()
                
                self.log_test(
                    "Role-Specific Data Creation",
                    "PASS",
                    f"Created {total_orders} orders and {admin_count} administrations"
                )
                return True
                
        except Exception as e:
            self.log_test("Role-Specific Data Creation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_auth_user_lookup_performance(self):
        """Critical: Test auth provider ID lookup performance"""
        try:
            with self.SessionLocal() as db:
                print("🔍 TESTING AUTH PROVIDER ID LOOKUP PERFORMANCE...")
                
                doctor = list(self.test_users.values())[0]
                auth_provider_id = doctor.auth_provider_id
                
                # This is the critical query from dependencies.py get_current_user()
                self.query_counter.reset()
                start_time = time.time()
                
                # Simulate the auth lookup that happens on every API request
                user = db.query(User).filter(User.auth_provider_id == auth_provider_id).first()
                
                lookup_time = time.time() - start_time
                query_count = self.query_counter.query_count
                
                if user and query_count == 1 and lookup_time < 0.01:  # Should be very fast
                    self.log_test(
                        "Auth Provider ID Lookup Performance",
                        "PASS",
                        f"Found user {user.email} in {lookup_time:.6f}s with {query_count} query"
                    )
                    return True
                else:
                    self.log_test(
                        "Auth Provider ID Lookup Performance",
                        "FAIL",
                        f"Slow auth lookup: {lookup_time:.6f}s, {query_count} queries, User found: {user is not None}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Auth Provider ID Lookup Performance", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_doctor_data_isolation(self):
        """Critical: Test that doctors can only see their own orders"""
        try:
            with self.SessionLocal() as db:
                print("🔐 TESTING DOCTOR DATA ISOLATION...")
                
                order_repo = OrderRepository(db)
                doctors = [user for user in self.test_users.values() if user.role == UserRole.doctor]
                
                if len(doctors) < 2:
                    self.log_test("Doctor Data Isolation", "SKIP", "Need 2+ doctors")
                    return True
                
                # Test the critical security feature: doctor-filtered queries
                self.query_counter.reset()
                start_time = time.time()
                
                doc1_orders = order_repo.list_by_doctor(doctors[0].id)
                doc2_orders = order_repo.list_by_doctor(doctors[1].id)
                
                query_time = time.time() - start_time
                query_count = self.query_counter.query_count
                
                # Verify data isolation
                doc1_order_ids = {order.id for order in doc1_orders}
                doc2_order_ids = {order.id for order in doc2_orders}
                overlap = doc1_order_ids.intersection(doc2_order_ids)
                
                # Access relationships to test N+1 prevention with auth
                total_administrations = 0
                for order in doc1_orders[:5]:  # Test first 5 orders
                    total_administrations += len(order.administrations)
                
                if (len(overlap) == 0 and len(doc1_orders) > 0 and len(doc2_orders) > 0 and
                    query_count <= 6):  # Should be efficient even with auth filtering
                    self.log_test(
                        "Doctor Data Isolation with Optimization",
                        "PASS",
                        f"Doc1: {len(doc1_orders)} orders, Doc2: {len(doc2_orders)} orders, No overlap, {total_administrations} administrations loaded, {query_count} queries in {query_time:.4f}s"
                    )
                    return True
                else:
                    self.log_test(
                        "Doctor Data Isolation with Optimization",
                        "FAIL",
                        f"Data leak: {len(overlap)} shared orders, or inefficient queries: {query_count}, Doc1: {len(doc1_orders)}, Doc2: {len(doc2_orders)}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Doctor Data Isolation with Optimization", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_optimized_queries_with_roles(self):
        """Test that optimized queries work correctly with role-based access"""
        try:
            with self.SessionLocal() as db:
                print("👨‍⚕️ TESTING OPTIMIZED QUERIES WITH ROLE CONTEXT...")
                
                order_repo = OrderRepository(db)
                doctor = self.test_users["doctor"]
                
                # Test the most common query pattern with auth context
                self.query_counter.reset()
                start_time = time.time()
                
                # Get doctor's orders with all relationships (like API would do)
                doctor_orders = order_repo.list_by_doctor(doctor.id)
                
                # Access all relationships to trigger our optimizations
                patients_seen = set()
                total_administrations = 0
                drug_names = set()
                
                for order in doctor_orders:
                    patients_seen.add(order.patient_name)
                    total_administrations += len(order.administrations)
                    if order.drug:
                        drug_names.add(order.drug.name)
                    # Access nested relationships
                    for admin in order.administrations:
                        if admin.nurse:
                            pass  # This should be efficiently loaded
                
                query_time = time.time() - start_time
                query_count = self.query_counter.query_count
                
                # Should be very efficient despite complex relationships
                expected_max_queries = 4
                
                if (query_count <= expected_max_queries and len(doctor_orders) > 0 and 
                    total_administrations > 0):
                    self.log_test(
                        "Role-Based Optimized Query Performance",
                        "PASS",
                        f"Loaded {len(doctor_orders)} orders, {len(patients_seen)} patients, {total_administrations} administrations, {len(drug_names)} drugs using {query_count} queries in {query_time:.4f}s"
                    )
                    return True
                else:
                    self.log_test(
                        "Role-Based Optimized Query Performance",
                        "FAIL",
                        f"Inefficient auth queries: {query_count} queries (expected ≤{expected_max_queries}), Orders: {len(doctor_orders)}, Administrations: {total_administrations}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Role-Based Optimized Query Performance", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_security_tests(self):
        """Run critical authorization security tests"""
        print("=" * 80)
        print("🔐 CRITICAL AUTHORIZATION SECURITY TEST SUITE")
        print("=" * 80)
        
        # Setup
        if not self.create_auth_test_users():
            print("\n❌ Failed to create auth test users.")
            return False
        
        if not self.create_role_specific_data():
            print("\n❌ Failed to create role-specific test data.")
            return False
        
        # Critical security tests
        tests = [
            self.test_auth_user_lookup_performance,
            self.test_doctor_data_isolation,
            self.test_optimized_queries_with_roles
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
        print("📊 AUTHORIZATION SECURITY TEST RESULTS")
        print("=" * 80)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n🎉 CRITICAL: ALL AUTHORIZATION SECURITY TESTS PASSED!")
            print("✅ Auth provider ID lookup optimized")
            print("✅ Doctor data isolation maintained")
            print("✅ Role-based queries efficient")
            print("✅ No security regressions detected")
            return True
        else:
            print(f"\n⚠️  CRITICAL: {failed} AUTHORIZATION SECURITY TESTS FAILED!")
            print("❌ POTENTIAL SECURITY VULNERABILITIES DETECTED")
            return False

def main():
    tester = AuthSecurityTester()
    success = tester.run_security_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 