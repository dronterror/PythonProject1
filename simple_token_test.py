#!/usr/bin/env python3
"""
Simple interactive test to find working Keycloak credentials
"""
import requests
import json

KEYCLOAK_URL = "http://keycloak:8080"
REALM = "medlog-realm"
CLIENT_ID = "medlog-clients"

def test_token(username, password):
    """Test if username/password can get a token"""
    token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
    
    data = {
        'client_id': CLIENT_ID,
        'username': username,
        'password': password,
        'grant_type': 'password',
    }
    
    try:
        response = requests.post(token_url, data=data, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            return access_token
        else:
            return None
    except Exception:
        return None

def test_api_with_token(token):
    """Test API call with token"""
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get("http://backend:8000/drugs", headers=headers, timeout=5)
        return response.status_code == 200
    except:
        return False

# Common username patterns to try
test_patterns = [
    # Basic patterns
    "admin", "doctor", "nurse", "pharmacist",
    
    # Email patterns
    "admin@medlog.local", "doctor@medlog.local", "nurse@medlog.local", "pharmacist@medlog.local",
    "admin@example.com", "doctor@example.com", "nurse@example.com", "pharmacist@example.com",
    
    # Other patterns
    "testuser", "user1", "user2", "test",
]

# Common passwords to try
test_passwords = [
    "admin123", "password", "123456", "admin", "test123", 
    "doctor123", "nurse123", "pharmacist123",
    "Password123", "test", "123"
]

print("🔍 Testing Common Username/Password Combinations...")
print("=" * 60)

successful_logins = []

for username in test_patterns:
    for password in test_passwords:
        print(f"Testing: {username} / {password}", end=" ... ")
        token = test_token(username, password)
        
        if token:
            api_works = test_api_with_token(token)
            status = "✅ SUCCESS + API WORKS!" if api_works else "✅ TOKEN ONLY"
            print(status)
            successful_logins.append({
                'username': username,
                'password': password,
                'token_works': True,
                'api_works': api_works,
                'token': token[:50] + "..." if token else None
            })
            break  # Found working password for this user
        else:
            print("❌")

print("\n" + "=" * 60)
print("🎯 RESULTS:")
print("=" * 60)

if successful_logins:
    print(f"✅ Found {len(successful_logins)} working credentials:")
    for login in successful_logins:
        print(f"  👤 {login['username']} / {login['password']}")
        print(f"     Token: {'✅' if login['token_works'] else '❌'}")
        print(f"     API:   {'✅' if login['api_works'] else '❌'}")
        print()
else:
    print("❌ No working credentials found")
    print("\n💡 Please check your Keycloak users:")
    print("   1. Go to http://keycloak.medlog.local")
    print("   2. Login with admin credentials")
    print("   3. Go to 'Users' section")
    print("   4. Check existing usernames and reset passwords if needed")

print("=" * 60) 