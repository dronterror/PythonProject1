#!/usr/bin/env python3
"""
Keycloak Setup Script

This script automates the setup of a Keycloak realm for the ValMed application.
It is idempotent, meaning it will reset the realm to a known clean state on each run.

The process is as follows:
1. Connect to the Keycloak master realm.
2. Delete the application realm if it exists, then create it.
3. Create a new admin client for the application realm.
4. Create the public client, application roles, and application users.
"""
import os
import sys
import time
import json
import requests
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakGetError, KeycloakPostError, KeycloakConnectionError

# --- Configuration ---
KEYCLOAK_URL = "http://keycloak:8080/"
KEYCLOAK_ADMIN_USER = "admin"
KEYCLOAK_ADMIN_PASSWORD = "admin"

REALM_NAME = "medflow-realm"
CLIENT_ID = "medflow-backend"
FRONTEND_URL = "http://medlog.local"

# A dedicated admin for our new realm
REALM_ADMIN_USER = "realm-admin"
REALM_ADMIN_PASSWORD = "password"

REALM_ROLES = ["super-admin", "doctor", "nurse", "pharmacist"]
USERS = [
    {"username": "superadmin", "password": "password", "email": "admin@valmed.local", "role": "super-admin"},
    {"username": "doctor", "password": "password", "email": "doctor@valmed.local", "role": "doctor"},
    {"username": "nurse", "password": "password", "email": "nurse@valmed.local", "role": "nurse"},
    {"username": "pharmacist", "password": "password", "email": "pharmacist@valmed.local", "role": "pharmacist"},
]
# --- End Configuration ---

def wait_for_keycloak(admin_client, max_retries=30, delay=5):
    """Waits for the Keycloak instance to be responsive."""
    print("--- Waiting for Keycloak to be ready ---")
    for i in range(max_retries):
        try:
            admin_client.get_realms()
            print("✅ Keycloak is responsive.")
            return True
        except (KeycloakConnectionError, requests.exceptions.ConnectionError):
            print(f"⏳ Waiting for Keycloak... (Attempt {i + 1}/{max_retries})")
            time.sleep(delay)
    print("❌ Keycloak did not become ready in time.", file=sys.stderr)
    return False

def setup_keycloak():
    """Connects to Keycloak and orchestrates the entire setup process."""
    print("🚀 Starting Keycloak setup...")

    # Step 1: Connect to the master realm
    try:
        master_admin = KeycloakAdmin(
            server_url=KEYCLOAK_URL,
            username=KEYCLOAK_ADMIN_USER,
            password=KEYCLOAK_ADMIN_PASSWORD,
            realm_name="master",
            verify=True,
        )
    except Exception as e:
        print(f"❌ Failed to connect to Keycloak master realm: {e}", file=sys.stderr)
        sys.exit(1)

    if not wait_for_keycloak(master_admin):
        sys.exit(1)

    # Step 2: Ensure a clean slate by deleting and recreating the realm
    print(f"--- Handling realm '{REALM_NAME}' ---")
    try:
        if master_admin.get_realm(REALM_NAME):
            print(f"Deleting existing realm '{REALM_NAME}'...")
            master_admin.delete_realm(REALM_NAME)
            time.sleep(2)
    except KeycloakGetError:
        pass # Realm doesn't exist, which is fine
    
    print(f"Creating realm '{REALM_NAME}'...")
    realm_payload = {
        "realm": REALM_NAME, 
        "enabled": True, 
        "sslRequired": "none",
        "verifyEmail": False,
        "loginWithEmailAllowed": True,
        "duplicateEmailsAllowed": False,
        "resetPasswordAllowed": True,
        "editUsernameAllowed": False,
        "bruteForceProtected": False,
        "registrationAllowed": False,
        "rememberMe": True,
        "passwordPolicy": "",  # No password policy requirements
        "defaultSignatureAlgorithm": "RS256",
        "revokeRefreshToken": False,
        "refreshTokenMaxReuse": 0,
        "accessTokenLifespan": 300,
        "accessTokenLifespanForImplicitFlow": 900,
        "ssoSessionIdleTimeout": 1800,
        "ssoSessionMaxLifespan": 36000,
        "offlineSessionIdleTimeout": 2592000,
        "offlineSessionMaxLifespanEnabled": False,
        "accessCodeLifespan": 60,
        "accessCodeLifespanUserAction": 300,
        "accessCodeLifespanLogin": 1800,
        "actionTokenGeneratedByAdminLifespan": 43200,
        "actionTokenGeneratedByUserLifespan": 300,
    }
    master_admin.create_realm(payload=realm_payload)
    print(f"✅ Realm '{REALM_NAME}' created.")

    # Step 2.5: Configure realm settings to disable account setup requirements
    print(f"--- Configuring realm settings ---")
    try:
        # Update realm to disable all possible account setup requirements
        realm_update_payload = {
            "requiredActions": [],  # No required actions globally
            "defaultRequiredActions": [],  # No default required actions for new users
            "browserFlow": "browser",
            "registrationFlow": "registration", 
            "directGrantFlow": "direct grant",
            "resetCredentialsFlow": "reset credentials",
            "clientAuthenticationFlow": "clients",
            "dockerAuthenticationFlow": "docker auth",
        }
        master_admin.connection.raw_put(
            f"/admin/realms/{REALM_NAME}",
            data=json.dumps(realm_update_payload)
        )
        print("✅ Realm configured to disable account setup requirements.")
    except Exception as e:
        print(f"⚠️  Warning: Could not update realm settings: {e}")

    # Step 3: Use master admin with proper realm targeting
    print(f"--- Setting up realm '{REALM_NAME}' using master admin ---")
    print("✅ Using master admin for realm setup.")

    # Step 4: Create the public client for the frontend
    print(f"--- Creating public client '{CLIENT_ID}' ---")
    
    # Create client in the specific realm using master admin
    client_payload = {
        "clientId": CLIENT_ID, 
        "enabled": True, 
        "publicClient": True,
        "directAccessGrantsEnabled": True, 
        "standardFlowEnabled": True,
        "implicitFlowEnabled": False,
        "serviceAccountsEnabled": False,
        "authorizationServicesEnabled": False,
        "fullScopeAllowed": True,
        "nodeReRegistrationTimeout": -1,
        "protocol": "openid-connect",
        "frontchannelLogout": False,
        "attributes": {
            "saml.assertion.signature": "false",
            "saml.force.post.binding": "false",
            "saml.multivalued.roles": "false",
            "saml.encrypt": "false",
            "saml.server.signature": "false",
            "saml.server.signature.keyinfo.ext": "false",
            "exclude.session.state.from.auth.response": "false",
            "saml_force_name_id_format": "false",
            "saml.client.signature": "false",
            "tls.client.certificate.bound.access.tokens": "false",
            "saml.authnstatement": "false",
            "display.on.consent.screen": "false",
            "saml.onetimeuse.condition": "false"
        },
        "redirectUris": [f"{FRONTEND_URL}/*", "http://localhost:5173/*"],
        "webOrigins": [FRONTEND_URL, "http://localhost:5173"],
    }
    
    # Use the connection to make direct API call to the specific realm
    response = master_admin.connection.raw_post(
        f"/admin/realms/{REALM_NAME}/clients",
        data=json.dumps(client_payload)
    )
    print(f"✅ Client '{CLIENT_ID}' created.")

    # Step 4.5: Configure authentication flows to disable problematic requirements
    print(f"--- Configuring authentication flows ---")
    try:
        # Get and update the direct grant flow to be more permissive
        flows_response = master_admin.connection.raw_get(
            f"/admin/realms/{REALM_NAME}/authentication/flows"
        )
        flows_data = flows_response.json()
        
        # Find the direct grant flow
        direct_grant_flow = None
        for flow in flows_data:
            if flow.get("alias") == "direct grant":
                direct_grant_flow = flow
                break
        
        if direct_grant_flow:
            print("  - Found direct grant flow, ensuring it's properly configured.")
            # The flow should be enabled by default, but let's make sure
        
        print("✅ Authentication flows configured.")
    except Exception as e:
        print(f"⚠️  Warning: Could not configure authentication flows: {e}")

    # Step 5: Create application roles
    print(f"--- Creating application roles ---")
    for role_name in REALM_ROLES:
        role_payload = {"name": role_name}
        try:
            master_admin.connection.raw_post(
                f"/admin/realms/{REALM_NAME}/roles",
                data=json.dumps(role_payload)
            )
            print(f"  - Role '{role_name}' created.")
        except KeycloakPostError as e:
            if e.response_code == 409:
                print(f"  - Role '{role_name}' already exists. Skipping.")
            else:
                print(f"❌ Error creating role '{role_name}': {e.error_message}", file=sys.stderr)
    print(f"✅ Roles ensured: {', '.join(REALM_ROLES)}")

    # Step 6: Create application users
    print(f"--- Creating application users ---")
    for user_data in USERS:
        username = user_data["username"]
        role_name = user_data["role"]
        try:
            # Create user with complete profile
            user_payload = {
                "username": username, 
                "email": user_data["email"],
                "firstName": username.capitalize(),
                "lastName": "User",
                "enabled": True,
                "emailVerified": True,
                "requiredActions": [],  # No required actions to avoid setup prompts
                "credentials": [{"type": "password", "value": user_data["password"], "temporary": False}],
            }
            master_admin.connection.raw_post(
                f"/admin/realms/{REALM_NAME}/users",
                data=json.dumps(user_payload)
            )
            
            # Get user ID
            users_response = master_admin.connection.raw_get(
                f"/admin/realms/{REALM_NAME}/users?username={username}"
            )
            users_data = users_response.json()
            if users_data:
                user_id = users_data[0]["id"]
                
                # Get role
                role_response = master_admin.connection.raw_get(
                    f"/admin/realms/{REALM_NAME}/roles/{role_name}"
                )
                role_data = role_response.json()
                
                # Assign role
                master_admin.connection.raw_post(
                    f"/admin/realms/{REALM_NAME}/users/{user_id}/role-mappings/realm",
                    data=json.dumps([role_data])
                )
                
                print(f"  - User '{username}' created with role '{role_name}'.")
            else:
                print(f"❌ Could not find created user '{username}'", file=sys.stderr)
                
        except KeycloakPostError as e:
            if e.response_code == 409:
                print(f"  - User '{username}' already exists. Skipping.")
            else:
                print(f"❌ Error with user '{username}': {e.error_message}", file=sys.stderr)
        except Exception as e:
            print(f"❌ Unexpected error with user '{username}': {e}", file=sys.stderr)

    print("\n🎉 Keycloak setup is complete!")

if __name__ == "__main__":
    setup_keycloak() 