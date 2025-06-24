# Auth0 Production Tenant Setup Guide

## Overview
This guide provides step-by-step instructions for setting up a production-ready Auth0 tenant for the MedLogistics application.

## Prerequisites
- Auth0 account with appropriate subscription tier
- Production domain names configured (e.g., admin.medlog.app, api.medlog.app)
- SSL certificates in place

## Step 1: Create Production Auth0 Tenant

1. **Log into Auth0 Dashboard**
   - Navigate to https://manage.auth0.com
   - Create a new tenant for production (e.g., `medlog-prod`)

2. **Tenant Settings**
   - Go to Settings > General
   - Set **Tenant Display Name**: "MedLogistics Production"
   - Set **Support Email**: your-support@medlog.app
   - Enable **Use a custom domain** if using custom domain

## Step 2: Configure Single Page Application (Admin Frontend)

1. **Create Application**
   - Navigate to Applications > Create Application
   - Name: "MedLogistics Admin Frontend"
   - Type: Single Page Web Applications
   - Technology: React

2. **Application Settings**
   ```
   Allowed Callback URLs:
   https://admin.medlog.app,https://admin.medlog.app/callback

   Allowed Logout URLs:
   https://admin.medlog.app

   Allowed Web Origins:
   https://admin.medlog.app

   Allowed Origins (CORS):
   https://admin.medlog.app

   Token Endpoint Authentication Method: None
   ```

3. **Advanced Settings**
   - OAuth tab:
     - JsonWebToken Signature Algorithm: RS256
     - OIDC Conformant: Enabled
   - Grant Types:
     - [x] Implicit
     - [x] Authorization Code
     - [x] Refresh Token

4. **Save Application**
   - Copy the **Client ID** for environment variables

## Step 3: Configure API (Resource Server)

1. **Create API**
   - Navigate to APIs > Create API
   - Name: "MedLogistics Backend API"
   - Identifier: `https://api.medlog.app`
   - Signing Algorithm: RS256

2. **API Settings**
   ```
   Name: MedLogistics Backend API
   Identifier: https://api.medlog.app
   Signing Algorithm: RS256
   Allow Skipping User Consent: Enabled (for first-party applications)
   Allow Offline Access: Enabled
   Token Lifetime: 86400 seconds (24 hours)
   Token Lifetime for Web: 7200 seconds (2 hours)
   ```

3. **Scopes (Optional)**
   - Add scopes if needed for granular permissions:
     - `read:hospitals`
     - `write:hospitals`
     - `read:users`
     - `write:users`

## Step 4: Create User Roles

1. **Navigate to User Management > Roles**

2. **Create Roles**
   - **Super Admin**
     - Name: `super_admin`
     - Description: "Full system administration access"

   - **Pharmacist**
     - Name: `pharmacist`
     - Description: "Pharmacy staff with medication management access"

   - **Doctor**
     - Name: `doctor`
     - Description: "Medical staff with prescription access"

   - **Nurse**
     - Name: `nurse`
     - Description: "Nursing staff with medication administration access"

3. **Assign Permissions to Roles** (if using scopes)
   - Super Admin: All scopes
   - Others: Appropriate subset of scopes

## Step 5: Create Auth0 Action for Custom Claims

1. **Navigate to Actions > Flows**

2. **Select "Login" Flow**

3. **Create Custom Action**
   - Click "+" to add action
   - Select "Build Custom"
   - Name: "Add Roles to Token"
   - Trigger: Login / Post Login

4. **Action Code**
   ```javascript
   /**
   * Handler that will be called during the execution of a PostLogin flow.
   * @param {Event} event - Details about the user and the context in which they are logging in.
   * @param {PostLoginAPI} api - Interface whose methods can be used to change the behavior of the login.
   */
   exports.onExecutePostLogin = async (event, api) => {
     const namespace = 'https://api.medlog.app/';
     
     // Get user roles from app_metadata
     const roles = event.user.app_metadata?.roles || [];
     
     // Add roles to access token
     if (roles.length > 0) {
       api.accessToken.setCustomClaim(`${namespace}roles`, roles);
     }
     
     // Add user info to ID token
     api.idToken.setCustomClaim(`${namespace}roles`, roles);
     api.idToken.setCustomClaim(`${namespace}user_id`, event.user.user_id);
   };
   ```

5. **Deploy Action**
   - Click "Deploy"
   - Drag the action into the Login flow
   - Apply changes

## Step 6: Create Management API Application (M2M)

1. **Create Machine-to-Machine Application**
   - Navigate to Applications > Create Application
   - Name: "MedLogistics User Management"
   - Type: Machine to Machine Applications
   - Authorize for: Auth0 Management API

2. **Scopes Required**
   ```
   read:users
   create:users
   update:users
   read:user_metadata
   update:user_metadata
   read:roles
   create:roles
   update:roles
   read:role_members
   create:role_members
   ```

3. **Save Credentials**
   - Copy **Client ID** and **Client Secret**
   - These will be used for user migration

## Step 7: Configure Database Connection

1. **Navigate to Authentication > Database**

2. **Configure Username-Password-Authentication**
   - Name: Keep default or rename to "MedLogistics-Users"
   - Password Policy: Fair (or stricter)
   - Password Complexity: Enabled
   - Password Dictionary: Enabled
   - Password History: Enabled

3. **Login Settings**
   - Username: Disabled (use email only)
   - Signup: Disabled (admin-only invitation)

## Step 8: Security Settings

1. **Navigate to Security > Attack Protection**

2. **Configure Brute Force Protection**
   - Enabled: Yes
   - Max Attempts: 10
   - Block for: 15 minutes

3. **Configure Suspicious IP Throttling**
   - Enabled: Yes
   - Max Attempts per IP: 100 per hour

4. **Configure Breached Password Detection**
   - Enabled: Yes
   - Action: Block login and send email

## Step 9: Monitoring and Logging

1. **Navigate to Monitoring > Logs**

2. **Configure Log Streams** (if needed)
   - Set up log streaming to your monitoring service
   - Common destinations: Datadog, Splunk, AWS CloudWatch

3. **Configure Alerts**
   - Failed login attempts
   - Successful admin logins
   - API rate limit violations

## Step 10: Production Environment Variables

After completing the Auth0 setup, you'll have these values for your production environment:

```env
# Auth0 Configuration (Production)
AUTH0_DOMAIN=medlog-prod.auth0.com
AUTH0_API_AUDIENCE=https://api.medlog.app
AUTH0_MANAGEMENT_CLIENT_ID=your-m2m-client-id
AUTH0_MANAGEMENT_CLIENT_SECRET=your-m2m-client-secret

# Frontend Auth0 Configuration
VITE_AUTH0_DOMAIN=medlog-prod.auth0.com
VITE_AUTH0_CLIENT_ID=your-spa-client-id
VITE_AUTH0_API_AUDIENCE=https://api.medlog.app
```

## Security Checklist

- [ ] Custom domain configured with SSL
- [ ] Brute force protection enabled
- [ ] Suspicious IP throttling enabled
- [ ] Breached password detection enabled
- [ ] User signup disabled (invitation-only)
- [ ] Strong password policy configured
- [ ] Roles and permissions properly assigned
- [ ] Log monitoring configured
- [ ] Backup and recovery procedures documented

## Testing Checklist

- [ ] Test login flow with production URLs
- [ ] Verify custom claims in JWT tokens
- [ ] Test role-based access control
- [ ] Verify Management API functionality
- [ ] Test logout and token refresh
- [ ] Verify CORS configuration
- [ ] Test error scenarios (invalid credentials, expired tokens)

## Post-Deployment Monitoring

Monitor these Auth0 metrics:
- Login success/failure rates
- Token issuance rates
- API call volumes to Management API
- Failed authentication attempts
- Role assignment accuracy

## Support and Troubleshooting

Common issues and solutions:
1. **CORS errors**: Verify allowed origins match exactly
2. **Token validation failures**: Check audience and issuer settings
3. **Role claims missing**: Verify Action is deployed and in flow
4. **Management API errors**: Check M2M app scopes and credentials 