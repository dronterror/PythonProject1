# Keycloak Environment Setup

This document explains the environment variables needed for the Keycloak integration.

## Required Environment Variables

### Root Directory .env (Optional)
Create a `.env` file in the root directory with these Keycloak admin credentials:

```env
# Keycloak Admin Configuration
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=your_secure_admin_password_here
KC_DB_URL_DATABASE=keycloak_db
```

### Backend .env File
Create a `backend/.env` file with these settings:

```env
# Database Configuration
DATABASE_URL=postgresql://valmed:valmedpass@db:5432/valmed
POSTGRES_USER=valmed
POSTGRES_PASSWORD=valmedpass
POSTGRES_DB=valmed

# Keycloak OIDC Configuration
KEYCLOAK_SERVER_URL=http://keycloak.medlog.local
KEYCLOAK_REALM=medlog-realm
KEYCLOAK_CLIENT_ID=medlog-clients

# Application Settings
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Security Settings
SECRET_KEY=your-secret-key-change-me-in-production
ALGORITHM=HS256
```

### Frontend Environment Variables
Update your `frontend-medlogistics/.env` file with:

```env
# Keycloak Configuration for Frontend
VITE_KEYCLOAK_URL=http://keycloak.medlog.local
VITE_KEYCLOAK_REALM=medlog-realm
VITE_KEYCLOAK_CLIENT_ID=medlog-clients
VITE_API_BASE_URL=http://localhost/api
```

## Docker Compose Environment Variables

The `docker-compose.yml` file uses these environment variables with default fallbacks:

- `KEYCLOAK_ADMIN` (default: admin)
- `KEYCLOAK_ADMIN_PASSWORD` (default: admin)
- `KC_DB_URL_DATABASE` (default: keycloak_db)

## Security Notes

1. **Change Default Passwords**: Never use the default admin password in production
2. **Use Strong Secrets**: Generate secure random strings for SECRET_KEY
3. **HTTPS in Production**: Use HTTPS URLs for all Keycloak and API endpoints in production
4. **Database Security**: Use strong database passwords and restrict access

## Migration from Auth0

If you're migrating from Auth0:

1. The database migration will rename `auth0_user_id` to `auth_provider_id`
2. Update any existing user records with Keycloak user IDs
3. Remove old Auth0 environment variables:
   - `AUTH0_DOMAIN`
   - `AUTH0_API_AUDIENCE`
   - `AUTH0_MANAGEMENT_CLIENT_ID`
   - `AUTH0_MANAGEMENT_CLIENT_SECRET`

## Quick Start

1. Copy environment templates above
2. Update passwords and secrets
3. Run `docker-compose up --build`
4. Follow the Keycloak setup instructions in README.md 