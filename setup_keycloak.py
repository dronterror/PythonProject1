#!/usr/bin/env python3
"""
Keycloak Setup Script
Automatically creates realm, client, roles, and users for MedLogistics
"""
import requests
import json
import time

# Configuration
KEYCLOAK_URL = "http://keycloak:8080"  # Internal Docker network
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"
REALM_NAME = "medlog-realm"
CLIENT_ID = "medlog-clients"

def get_admin_token():
    """Get admin access token"""
    url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    data = {
        'client_id': 'admin-cli',
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD,
        'grant_type': 'password',
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Failed to get admin token: {response.status_code}")
        print(response.text)
        return None

def create_realm(token):
    """Create the medlog-realm"""
    url = f"{KEYCLOAK_URL}/admin/realms"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    realm_config = {
        "realm": REALM_NAME,
        "enabled": True,
        "displayName": "MedLogistics Realm",
        "accessTokenLifespan": 300,
        "refreshTokenMaxReuse": 0,
        "sslRequired": "none",
        "directGrantFlow": "direct grant"
    }
    
    response = requests.post(url, headers=headers, json=realm_config)
    if response.status_code == 201:
        print(f"✅ Realm '{REALM_NAME}' created successfully")
        return True
    elif response.status_code == 409:
        print(f"ℹ️  Realm '{REALM_NAME}' already exists")
        return True
    else:
        print(f"❌ Failed to create realm: {response.status_code}")
        print(response.text)
        return False

def create_client(token):
    """Create the medlog-clients client"""
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    client_config = {
        "clientId": CLIENT_ID,
        "enabled": True,
        "publicClient": True,
        "directAccessGrantsEnabled": True,
        "standardFlowEnabled": True,
        "implicitFlowEnabled": False,
        "serviceAccountsEnabled": False,
        "redirectUris": [
            "http://medlog.local/*",
            "http://localhost:3000/*",
            "http://localhost:5173/*"
        ],
        "webOrigins": [
            "http://medlog.local",
            "http://localhost:3000",
            "http://localhost:5173"
        ],
        "attributes": {
            "access.token.lifespan": "300"
        }
    }
    
    response = requests.post(url, headers=headers, json=client_config)
    if response.status_code == 201:
        print(f"✅ Client '{CLIENT_ID}' created successfully")
        return True
    elif response.status_code == 409:
        print(f"ℹ️  Client '{CLIENT_ID}' already exists")
        return True
    else:
        print(f"❌ Failed to create client: {response.status_code}")
        print(response.text)
        return False

def create_roles(token):
    """Create realm roles"""
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/roles"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    roles = [
        {"name": "super-admin", "description": "Super Administrator"},
        {"name": "doctor", "description": "Doctor"},
        {"name": "nurse", "description": "Nurse"},
        {"name": "pharmacist", "description": "Pharmacist"}
    ]
    
    for role in roles:
        response = requests.post(url, headers=headers, json=role)
        if response.status_code == 201:
            print(f"✅ Role '{role['name']}' created successfully")
        elif response.status_code == 409:
            print(f"ℹ️  Role '{role['name']}' already exists")
        else:
            print(f"❌ Failed to create role '{role['name']}': {response.status_code}")

def create_user(token, username, password, roles):
    """Create a user with specified roles"""
    # Create user
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    user_config = {
        "username": username,
        "enabled": True,
        "emailVerified": True,
        "email": f"{username}@medlog.local",
        "firstName": username.title(),
        "lastName": "User",
        "credentials": [{
            "type": "password",
            "value": password,
            "temporary": False
        }]
    }
    
    response = requests.post(url, headers=headers, json=user_config)
    if response.status_code == 201:
        print(f"✅ User '{username}' created successfully")
        
        # Get user ID
        user_id = response.headers.get('Location').split('/')[-1]
        
        # Assign roles
        assign_roles_to_user(token, user_id, roles)
        return True
    elif response.status_code == 409:
        print(f"ℹ️  User '{username}' already exists")
        return True
    else:
        print(f"❌ Failed to create user '{username}': {response.status_code}")
        print(response.text)
        return False

def assign_roles_to_user(token, user_id, role_names):
    """Assign roles to a user"""
    # Get role objects
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    roles_to_assign = []
    for role_name in role_names:
        role_url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/roles/{role_name}"
        response = requests.get(role_url, headers=headers)
        if response.status_code == 200:
            roles_to_assign.append(response.json())
    
    # Assign roles
    if roles_to_assign:
        assign_url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{user_id}/role-mappings/realm"
        response = requests.post(assign_url, headers=headers, json=roles_to_assign)
        if response.status_code == 204:
            print(f"✅ Roles assigned to user: {[r['name'] for r in roles_to_assign]}")
        else:
            print(f"❌ Failed to assign roles: {response.status_code}")

def main():
    print("🚀 Setting up Keycloak for MedLogistics...")
    
    # Wait for Keycloak to be ready
    print("⏳ Waiting for Keycloak to be ready...")
    time.sleep(5)
    
    # Get admin token
    print("🔑 Getting admin token...")
    token = get_admin_token()
    if not token:
        print("❌ Failed to get admin token. Exiting.")
        return False
    
    # Create realm
    print("🏗️  Creating realm...")
    if not create_realm(token):
        return False
    
    # Create client
    print("🔧 Creating client...")
    if not create_client(token):
        return False
    
    # Create roles
    print("👥 Creating roles...")
    create_roles(token)
    
    # Create users
    print("👤 Creating users...")
    users = [
        ("admin", "admin", ["super-admin"]),
        ("doctor", "doctor", ["doctor"]),
        ("nurse", "nurse", ["nurse"]),
        ("pharmacist", "pharmacist", ["pharmacist"])
    ]
    
    for username, password, roles in users:
        create_user(token, username, password, roles)
    
    print("\n🎉 Keycloak setup complete!")
    print("\n📋 Summary:")
    print(f"   Realm: {REALM_NAME}")
    print(f"   Client: {CLIENT_ID}")
    print("   Users created:")
    print("   - admin/admin (super-admin)")
    print("   - doctor/doctor (doctor)")
    print("   - nurse/nurse (nurse)")
    print("   - pharmacist/pharmacist (pharmacist)")
    print(f"\n🌐 Access: http://keycloak.medlog.local")
    print(f"🔗 Admin: http://localhost:8081")
    
    return True

if __name__ == "__main__":
    main() 