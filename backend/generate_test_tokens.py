#!/usr/bin/env python3
"""
Generate JWT tokens for testing the migrated authentication system
"""

import jwt
import json
from datetime import datetime, timedelta
from database import SessionLocal
from models import User

# JWT Configuration (matches .env file)
JWT_SECRET_KEY = "your-super-secret-jwt-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def generate_tokens_for_all_users():
    """Generate JWT tokens for all users in the database"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        tokens = {}
        
        print("🔑 Generating JWT tokens for all users...")
        print("="*60)
        
        for user in users:
            # Create token payload
            token_data = {
                "sub": user.auth0_user_id,  # Subject (Auth0 user ID)
                "email": user.email,
                "role": user.role.value,
                "iat": datetime.utcnow(),
                "iss": "https://dev-medlog-test.us.auth0.com/",
                "aud": "https://api.medlog.app"
            }
            
            # Generate token
            token = create_access_token(token_data)
            tokens[user.role.value] = {
                "email": user.email,
                "token": token,
                "auth0_user_id": user.auth0_user_id
            }
            
            print(f"✓ {user.email} ({user.role.value})")
            print(f"  Auth0 ID: {user.auth0_user_id}")
            print(f"  Token: {token}")
            print()
        
        return tokens
        
    finally:
        db.close()

def main():
    """Main function"""
    print("🚀 JWT Token Generator for MedLogistics")
    print("Generating tokens for testing the migrated authentication system\n")
    
    tokens = generate_tokens_for_all_users()
    
    print("="*60)
    print("📋 SUMMARY - Copy these tokens for frontend testing:")
    print("="*60)
    
    for role, data in tokens.items():
        print(f"\n{role.upper()} TOKEN:")
        print(f"Email: {data['email']}")
        print(f"Token: {data['token']}")
    
    print("\n🔧 FRONTEND INTEGRATION:")
    print("Replace 'X-API-Key' headers with 'Authorization: Bearer <token>'")
    print("Example:")
    print("  OLD: headers: {'X-API-Key': 'admin_key_001'}")
    print("  NEW: headers: {'Authorization': 'Bearer <token_from_above>'}")
    
    print("\n✅ All tokens generated successfully!")

if __name__ == "__main__":
    main() 