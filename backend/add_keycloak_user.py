#!/usr/bin/env python3
"""
Simple script to add existing Keycloak users to the database.
Use this for users you've already created in Keycloak Admin Console.
"""

import sys
import uuid
from database import SessionLocal
from models import User, UserRole

def add_keycloak_user(email: str, role: str, keycloak_user_id: str):
    """Add a Keycloak user to the database."""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User {email} already exists in database!")
            return
        
        # Validate role
        try:
            user_role = UserRole(role)
        except ValueError:
            print(f"Invalid role: {role}. Valid roles: {[r.value for r in UserRole]}")
            return
        
        # Create user
        new_user = User(
            id=uuid.uuid4(),
            email=email,
            role=user_role,
            auth_provider_id=keycloak_user_id
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Added user: {new_user.email}")
        print(f"   Database ID: {new_user.id}")
        print(f"   Role: {new_user.role.value}")
        print(f"   Keycloak ID: {new_user.auth_provider_id}")
        
    except Exception as e:
        print(f"❌ Failed to add user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Example usage - modify these values for your actual Keycloak users
    print("Adding sample Keycloak users to database...")
    print("Note: Replace these with your actual Keycloak user details")
    print()
    
    # Add your actual Keycloak users here
    # You can find the Keycloak user IDs in the Keycloak Admin Console
    users_to_add = [
        {
            "email": "doctor@hospital.com",
            "role": "doctor",
            "keycloak_user_id": "keycloak-user-id-1"  # Replace with actual Keycloak ID
        },
        {
            "email": "nurse@hospital.com", 
            "role": "nurse",
            "keycloak_user_id": "keycloak-user-id-2"  # Replace with actual Keycloak ID
        },
        {
            "email": "pharmacist@hospital.com",
            "role": "pharmacist", 
            "keycloak_user_id": "keycloak-user-id-3"  # Replace with actual Keycloak ID
        }
    ]
    
    for user_data in users_to_add:
        add_keycloak_user(
            email=user_data["email"],
            role=user_data["role"],
            keycloak_user_id=user_data["keycloak_user_id"]
        )
        print()
    
    print("Done! Users can now log in and access /api/v1/users/me") 