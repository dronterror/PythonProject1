#!/usr/bin/env python3
"""
ValMed Medication Logistics - Secure Database Seeding Script

This script creates a secure, reproducible demo database with:
- Three users (pharmacist, doctor, nurse) with cryptographically secure API keys
- Sample drugs with realistic stock levels
- Proper role-based access control setup

Usage:
    python seed_db.py

Author: ValMed Development Team
Version: 1.0.0
"""

import secrets
import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend import crud, schemas, models, database
from backend.models import UserRole

def generate_secure_api_key():
    """Generate a cryptographically secure API key"""
    return secrets.token_hex(32)

def create_demo_users(db):
    """Create three demo users with secure API keys"""
    users_data = [
        {
            "email": "pharmacist@valmed.com",
            "role": UserRole.pharmacist,
            "hashed_password": "hashed_password_123",  # In production, use proper password hashing
            "api_key": generate_secure_api_key()
        },
        {
            "email": "doctor@valmed.com", 
            "role": UserRole.doctor,
            "hashed_password": "hashed_password_123",
            "api_key": generate_secure_api_key()
        },
        {
            "email": "nurse@valmed.com",
            "role": UserRole.nurse,
            "hashed_password": "hashed_password_123", 
            "api_key": generate_secure_api_key()
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user_create = schemas.UserCreate(**user_data)
        user = crud.create_user(db, user_create)
        created_users.append(user)
        print(f"Created {user.role.value}: {user.email}")
    
    return created_users

def create_sample_drugs(db):
    """Create sample drugs with realistic stock levels"""
    drugs_data = [
        {
            "name": "Paracetamol",
            "form": "Tablet",
            "strength": "500mg",
            "current_stock": 150,
            "low_stock_threshold": 20
        },
        {
            "name": "Aspirin", 
            "form": "Tablet",
            "strength": "100mg",
            "current_stock": 200,
            "low_stock_threshold": 25
        },
        {
            "name": "Ibuprofen",
            "form": "Tablet", 
            "strength": "400mg",
            "current_stock": 75,
            "low_stock_threshold": 15
        },
        {
            "name": "Amoxicillin",
            "form": "Capsule",
            "strength": "250mg", 
            "current_stock": 50,
            "low_stock_threshold": 10
        },
        {
            "name": "Omeprazole",
            "form": "Capsule",
            "strength": "20mg",
            "current_stock": 30,
            "low_stock_threshold": 5
        }
    ]
    
    created_drugs = []
    for drug_data in drugs_data:
        drug_create = schemas.DrugCreate(**drug_data)
        drug = crud.create_drug(db, drug_create)
        created_drugs.append(drug)
        print(f"Created drug: {drug.name} {drug.strength} - Stock: {drug.current_stock}")
    
    return created_drugs

def main():
    """Main seeding function"""
    print("🌱 Starting ValMed Database Seeding...")
    print("=" * 50)
    
    # Create database session
    db = database.SessionLocal()
    
    try:
        # Check if database is empty
        existing_users = db.query(models.User).count()
        if existing_users > 0:
            print("⚠️  Database already contains data. Skipping seeding.")
            return
        
        # Create users
        print("\n👥 Creating demo users...")
        users = create_demo_users(db)
        
        # Create drugs
        print("\n💊 Creating sample drugs...")
        drugs = create_sample_drugs(db)
        
        # Print API keys for testing
        print("\n🔑 Generated API Keys for Testing:")
        print("=" * 50)
        for user in users:
            print(f"{user.role.value.capitalize()} API Key: {user.api_key}")
        
        print("\n✅ Database seeding completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Use the API keys above to test the endpoints")
        print("2. The system is now ready for pilot testing")
        print("3. Remember to change passwords in production")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main() 