#!/usr/bin/env python3
"""
Test script for collaborative API endpoints
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost/api"

def get_api_keys():
    """Get API keys from the database"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from database import SessionLocal
    from models import User
    
    db = SessionLocal()
    users = db.query(User).all()
    api_keys = {user.role.value: user.api_key for user in users}
    db.close()
    
    return api_keys

def test_endpoints():
    """Test the collaborative endpoints"""
    print("Testing Collaborative API Endpoints")
    print("=" * 50)
    
    # Get API keys
    api_keys = get_api_keys()
    print(f"Found API keys: {list(api_keys.keys())}")
    
    # Test 1: Doctor accessing their own orders
    print("\n1. Testing Doctor's My Orders Endpoint")
    print("-" * 40)
    
    headers = {"X-API-Key": api_keys.get("doctor", "test_key")}
    response = requests.get(f"{BASE_URL}/orders/my-orders/", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        orders = response.json()
        print(f"✅ Success! Found {len(orders)} orders for doctor")
        if orders:
            print(f"   First order: {orders[0]['patient_name']} - {orders[0]['status']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 2: Nurse accessing active MAR
    print("\n2. Testing Nurse's Active MAR Endpoint")
    print("-" * 40)
    
    headers = {"X-API-Key": api_keys.get("nurse", "test_key")}
    response = requests.get(f"{BASE_URL}/orders/active-mar/", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        orders = response.json()
        print(f"✅ Success! Found {len(orders)} active orders for MAR")
        if orders:
            print(f"   First order: {orders[0]['patient_name']} - {orders[0]['status']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 3: Pharmacist accessing active MAR
    print("\n3. Testing Pharmacist's Active MAR Endpoint")
    print("-" * 40)
    
    headers = {"X-API-Key": api_keys.get("pharmacist", "test_key")}
    response = requests.get(f"{BASE_URL}/orders/active-mar/", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        orders = response.json()
        print(f"✅ Success! Found {len(orders)} active orders for MAR")
        if orders:
            print(f"   First order: {orders[0]['patient_name']} - {orders[0]['status']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 4: Doctor trying to access MAR (should be denied)
    print("\n4. Testing Doctor Access to MAR (Should Be Denied)")
    print("-" * 40)
    
    headers = {"X-API-Key": api_keys.get("doctor", "test_key")}
    response = requests.get(f"{BASE_URL}/orders/active-mar/", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 403:
        print("✅ Success! Doctor correctly denied access to MAR")
    else:
        print(f"❌ Unexpected: {response.text}")
    
    # Test 5: Nurse trying to access doctor's orders (should be denied)
    print("\n5. Testing Nurse Access to Doctor's Orders (Should Be Denied)")
    print("-" * 40)
    
    headers = {"X-API-Key": api_keys.get("nurse", "test_key")}
    response = requests.get(f"{BASE_URL}/orders/my-orders/", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 403:
        print("✅ Success! Nurse correctly denied access to doctor's orders")
    else:
        print(f"❌ Unexpected: {response.text}")

if __name__ == "__main__":
    test_endpoints() 