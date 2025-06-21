#!/usr/bin/env python3
"""
Simple test script to verify collaborative functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dependencies import require_roles, require_role
from models import User, UserRole
from fastapi import HTTPException

def test_require_roles():
    """Test the new require_roles function"""
    print("Testing require_roles function...")
    
    # Create test users
    doctor = User(
        email="doctor@test.com",
        role=UserRole.doctor,
        api_key="doctor_key",
        hashed_password="password"
    )
    
    nurse = User(
        email="nurse@test.com", 
        role=UserRole.nurse,
        api_key="nurse_key",
        hashed_password="password"
    )
    
    pharmacist = User(
        email="pharmacist@test.com",
        role=UserRole.pharmacist, 
        api_key="pharmacist_key",
        hashed_password="password"
    )
    
    # Test nurse and pharmacist access
    nurse_pharmacist_dependency = require_roles(["nurse", "pharmacist"])
    
    try:
        result = nurse_pharmacist_dependency(current_user=nurse)
        print("✅ Nurse can access nurse/pharmacist endpoint")
    except Exception as e:
        print(f"❌ Nurse access failed: {e}")
    
    try:
        result = nurse_pharmacist_dependency(current_user=pharmacist)
        print("✅ Pharmacist can access nurse/pharmacist endpoint")
    except Exception as e:
        print(f"❌ Pharmacist access failed: {e}")
    
    try:
        result = nurse_pharmacist_dependency(current_user=doctor)
        print("❌ Doctor should not access nurse/pharmacist endpoint")
    except HTTPException as e:
        if e.status_code == 403:
            print("✅ Doctor correctly denied access to nurse/pharmacist endpoint")
        else:
            print(f"❌ Unexpected error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Test doctor-only access
    doctor_dependency = require_role("doctor")
    
    try:
        result = doctor_dependency(current_user=doctor)
        print("✅ Doctor can access doctor-only endpoint")
    except Exception as e:
        print(f"❌ Doctor access failed: {e}")
    
    try:
        result = doctor_dependency(current_user=nurse)
        print("❌ Nurse should not access doctor-only endpoint")
    except HTTPException as e:
        if e.status_code == 403:
            print("✅ Nurse correctly denied access to doctor-only endpoint")
        else:
            print(f"❌ Unexpected error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_schema_imports():
    """Test that schemas can be imported correctly"""
    print("\nTesting schema imports...")
    
    try:
        from schemas import MedicationOrderOut, MedicationAdministrationOut
        print("✅ MedicationOrderOut and MedicationAdministrationOut imported successfully")
        
        # Test that the schema has the administrations field
        if hasattr(MedicationOrderOut, 'administrations'):
            print("✅ MedicationOrderOut has administrations field")
        else:
            print("❌ MedicationOrderOut missing administrations field")
            
    except Exception as e:
        print(f"❌ Schema import failed: {e}")

def test_crud_imports():
    """Test that CRUD functions can be imported correctly"""
    print("\nTesting CRUD imports...")
    
    try:
        from crud import get_multi_by_doctor, get_multi_active
        print("✅ CRUD functions imported successfully")
    except Exception as e:
        print(f"❌ CRUD import failed: {e}")

if __name__ == "__main__":
    print("Testing Collaborative Read-Only Views Implementation")
    print("=" * 60)
    
    test_require_roles()
    test_schema_imports()
    test_crud_imports()
    
    print("\n" + "=" * 60)
    print("Test completed!") 