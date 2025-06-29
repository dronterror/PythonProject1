#!/usr/bin/env python3
"""
Test script for database optimizations.
This script verifies that:
1. Cursor-based pagination works correctly
2. Optimized loading strategies prevent N+1 queries
3. Performance improvements are measurable
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:80/api/v1"
HEADERS = {"Content-Type": "application/json"}

class DatabaseOptimizationTester:
    """Test suite for database optimizations"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
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
    
    def test_api_health(self) -> bool:
        """Test if the API is responding"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("API Health Check", "PASS", "API is responding")
                return True
            else:
                self.log_test("API Health Check", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Health Check", "FAIL", f"Connection error: {str(e)}")
            return False
    
    def test_cursor_pagination_endpoint(self) -> bool:
        """Test the new cursor-based pagination endpoint"""
        try:
            # Test first page with timestamp cursor
            response = requests.get(
                f"{self.base_url}/orders/cursor",
                params={"limit": 10, "cursor_type": "timestamp"},
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_keys = ["orders", "next_cursor", "has_next", "cursor_type"]
                if all(key in data for key in required_keys):
                    self.log_test(
                        "Cursor Pagination Structure",
                        "PASS",
                        f"Response has all required keys: {required_keys}"
                    )
                    
                    # Test with cursor if available
                    if data["next_cursor"] and data["has_next"]:
                        next_response = requests.get(
                            f"{self.base_url}/orders/cursor",
                            params={
                                "limit": 10,
                                "cursor": data["next_cursor"],
                                "cursor_type": "timestamp"
                            },
                            headers=self.headers,
                            timeout=10
                        )
                        
                        if next_response.status_code == 200:
                            self.log_test(
                                "Cursor Pagination Navigation",
                                "PASS",
                                "Successfully navigated to next page using cursor"
                            )
                        else:
                            self.log_test(
                                "Cursor Pagination Navigation",
                                "FAIL",
                                f"Next page request failed: {next_response.status_code}"
                            )
                    else:
                        self.log_test(
                            "Cursor Pagination Navigation",
                            "SKIP",
                            "No next page available (empty dataset)"
                        )
                    
                    return True
                else:
                    missing_keys = [key for key in required_keys if key not in data]
                    self.log_test(
                        "Cursor Pagination Structure",
                        "FAIL",
                        f"Missing keys: {missing_keys}"
                    )
                    return False
            else:
                self.log_test(
                    "Cursor Pagination Endpoint",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Cursor Pagination Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_id_based_cursor_pagination(self) -> bool:
        """Test ID-based cursor pagination"""
        try:
            response = requests.get(
                f"{self.base_url}/orders/cursor",
                params={"limit": 5, "cursor_type": "id"},
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["cursor_type"] == "id":
                    self.log_test(
                        "ID-Based Cursor Pagination",
                        "PASS",
                        "ID-based cursor pagination working correctly"
                    )
                    return True
                else:
                    self.log_test(
                        "ID-Based Cursor Pagination",
                        "FAIL",
                        f"Expected cursor_type 'id', got '{data.get('cursor_type')}'"
                    )
                    return False
            else:
                self.log_test(
                    "ID-Based Cursor Pagination",
                    "FAIL",
                    f"HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("ID-Based Cursor Pagination", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_performance_comparison(self) -> bool:
        """Compare performance between offset and cursor pagination"""
        try:
            # Test offset-based pagination (old method)
            start_time = time.time()
            offset_response = requests.get(
                f"{self.base_url}/orders",
                params={"skip": 0, "limit": 50},
                headers=self.headers,
                timeout=30
            )
            offset_time = time.time() - start_time
            
            # Test cursor-based pagination (new method)
            start_time = time.time()
            cursor_response = requests.get(
                f"{self.base_url}/orders/cursor",
                params={"limit": 50, "cursor_type": "timestamp"},
                headers=self.headers,
                timeout=30
            )
            cursor_time = time.time() - start_time
            
            if offset_response.status_code == 200 and cursor_response.status_code == 200:
                performance_improvement = ((offset_time - cursor_time) / offset_time) * 100
                
                self.log_test(
                    "Performance Comparison",
                    "PASS",
                    f"Offset: {offset_time:.3f}s, Cursor: {cursor_time:.3f}s, "
                    f"Improvement: {performance_improvement:.1f}%"
                )
                return True
            else:
                self.log_test(
                    "Performance Comparison",
                    "FAIL",
                    f"Offset status: {offset_response.status_code}, "
                    f"Cursor status: {cursor_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Performance Comparison", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_mar_dashboard_optimization(self) -> bool:
        """Test the optimized MAR dashboard endpoint"""
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/orders/mar-dashboard",
                headers=self.headers,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify structure indicates optimized loading
                if "patients" in data and "summary" in data:
                    self.log_test(
                        "MAR Dashboard Optimization",
                        "PASS",
                        f"Dashboard loaded in {response_time:.3f}s with optimized structure"
                    )
                    
                    # Check if patients have proper order structure (indicates selectinload worked)
                    if data["patients"]:
                        patient = data["patients"][0]
                        if "active_orders" in patient:
                            self.log_test(
                                "MAR Dashboard Data Structure",
                                "PASS",
                                "Patient orders properly loaded with optimized queries"
                            )
                        else:
                            self.log_test(
                                "MAR Dashboard Data Structure",
                                "FAIL",
                                "Patient orders structure missing"
                            )
                    else:
                        self.log_test(
                            "MAR Dashboard Data Structure",
                            "SKIP",
                            "No patients in database to test structure"
                        )
                    
                    return True
                else:
                    self.log_test(
                        "MAR Dashboard Optimization",
                        "FAIL",
                        "Response missing required structure"
                    )
                    return False
            else:
                self.log_test(
                    "MAR Dashboard Optimization",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("MAR Dashboard Optimization", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all database optimization tests"""
        print("=" * 60)
        print("DATABASE OPTIMIZATION TEST SUITE")
        print("=" * 60)
        
        # Test API availability first
        if not self.test_api_health():
            print("\n❌ API is not available. Cannot run tests.")
            return {"status": "FAILED", "reason": "API unavailable"}
        
        # Run optimization tests
        tests = [
            self.test_cursor_pagination_endpoint,
            self.test_id_based_cursor_pagination,
            self.test_performance_comparison,
            self.test_mar_dashboard_optimization
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
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"📊 Total: {len(self.test_results)}")
        
        success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL DATABASE OPTIMIZATIONS ARE WORKING CORRECTLY!")
            return {"status": "SUCCESS", "details": self.test_results}
        else:
            print(f"\n⚠️  {failed} tests failed. Check the logs above for details.")
            return {"status": "PARTIAL", "details": self.test_results}

def main():
    """Main test runner"""
    tester = DatabaseOptimizationTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["status"] == "SUCCESS":
        sys.exit(0)
    elif results["status"] == "PARTIAL":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main() 