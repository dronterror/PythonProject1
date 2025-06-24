#!/usr/bin/env python3
"""
Simple JWT Token Generator for MedLogistics
Uses raw SQL to avoid ORM issues
"""

import jwt
from datetime import datetime, timedelta
from database import SessionLocal
from sqlalchemy import text

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

def main():
    """Generate JWT tokens for all users"""
    print("🚀 JWT Token Generator for MedLogistics")
    print("Generating tokens for testing the migrated authentication system\n")
    
    db = SessionLocal()
    try:
        # Get users using raw SQL
        result = db.execute(text('SELECT email, auth0_user_id, role FROM users')).fetchall()
        
        print("🔑 Generating JWT tokens for all users...")
        print("="*60)
        
        tokens = {}
        
        for row in result:
            email, auth0_user_id, role = row
            
            # Create token payload
            token_data = {
                "sub": auth0_user_id,  # Subject (Auth0 user ID)
                "email": email,
                "role": role,
                "iat": datetime.utcnow(),
                "iss": "https://dev-medlog-test.us.auth0.com/",
                "aud": "https://api.medlog.app"
            }
            
            # Generate token
            token = create_access_token(token_data)
            tokens[role] = {
                "email": email,
                "token": token,
                "auth0_user_id": auth0_user_id
            }
            
            print(f"✓ {email} ({role})")
            print(f"  Auth0 ID: {auth0_user_id}")
            print(f"  Token: {token}")
            print()
        
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
        
    finally:
        db.close()

if __name__ == "__main__":
    main() 