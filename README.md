# ValMed - Multi-Role Medication Logistics Platform

A comprehensive medication logistics platform with unified frontend supporting multiple roles and a robust backend with Auth0 authentication.

## Architecture

- **Frontend**: Unified React PWA with TypeScript, MUI, role-based routing and interfaces
- **Backend**: FastAPI with PostgreSQL, Auth0 authentication, and comprehensive RBAC
- **Reverse Proxy**: Traefik for routing and load balancing
- **Containerization**: Docker Compose for easy deployment

## Roles & Interfaces

- **Super Admin**: Hospital & user management, permissions, system oversight
- **Doctor**: Mobile-first PWA for prescription management and order tracking
- **Pharmacist**: Mobile-first PWA for inventory management and alerts
- **Nurse**: Mobile-first PWA for medication administration and patient care

## Development Workflow

### One-Time Setup

1. **Install Poetry** (Python dependency manager):
   ```bash
   # On Windows (PowerShell):
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   
   # On Linux/macOS:
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Clone and setup**:
   ```bash
   git clone <repository>
   cd ValMed/backend
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Create environment files**:
   ```bash
   # Create backend environment file (see KEYCLOAK_ENVIRONMENT_SETUP.md for templates)
   cp backend/.env.example backend/.env
   # Edit backend/.env with your Keycloak and database settings
   
   # Optionally create root .env for Keycloak admin credentials
   # See KEYCLOAK_ENVIRONMENT_SETUP.md for required variables
   ```

### Local Development

1. **Activate Poetry shell**:
   ```bash
   poetry shell
   ```

2. **Database Migrations** (run migrations for the first time):
   ```bash
   poetry run alembic upgrade head
   ```

3. **Run the application**:
   ```bash
   poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Run tests**:
   ```bash
   poetry run pytest
   ```

### Database Migrations

- **Create a new migration** (after changing models):
  ```bash
  poetry run alembic revision --autogenerate -m "Description of changes"
  ```

- **Apply migrations**:
  ```bash
  poetry run alembic upgrade head
  ```

- **Rollback migrations**:
  ```bash
  poetry run alembic downgrade -1
  ```

### Docker Workflow

1. **Add hosts entries** (Windows: edit `C:\Windows\System32\drivers\etc\hosts`):
   ```
   127.0.0.1 medlog.local api.medlog.local keycloak.medlog.local
   ```

2. **Build and run with Docker**:
   ```bash
   docker-compose up --build
   ```

3. **Run database migrations in Docker**:
   ```bash
   docker-compose run --rm api poetry run alembic upgrade head
   ```

4. **Access the application**:
   - Frontend: http://medlog.local (unified interface for all roles)
   - Backend API: http://api.medlog.local  
   - Keycloak Admin Console: http://keycloak.medlog.local
   - Traefik Dashboard: http://localhost:8080

### Keycloak Initial Setup (One-Time Task)

After running `docker-compose up` for the first time, you must configure Keycloak.

1. **Access Keycloak:** Navigate to `http://keycloak.medlog.local` and click on "Administration Console".
2. **Log In:** Use the admin credentials you set in your `.env` file (default: `admin`/`admin`).
3. **Create a Realm:**
   - Hover over the "master" realm name in the top-left and click "Create Realm".
   - **Realm name:** `medlog-realm`. Click "Create".
4. **Create a Client for Your Frontends:**
   - In the `medlog-realm`, go to `Clients` and click "Create client".
   - **Client ID:** `medlog-clients`.
   - **Valid Redirect URIs:** Add `http://medlog.local/*`, `http://localhost/*`.
   - Leave other settings as default for now and save.
5. **Create Roles:**
   - Go to `Realm Roles` and click "Create role".
   - Create the following roles: `super-admin`, `pharmacist`, `doctor`, `nurse`.
6. **Create a Test User:**
   - Go to `Users` and click "Add user".
   - Enter an email and toggle "Email verified" to ON. Save.
   - Go to the "Credentials" tab for the new user and set a password.
   - Go to the "Role mapping" tab and assign a realm role (e.g., `pharmacist`).
7. **(Optional but Recommended) Add Roles to Token:**
   - Go to `Clients` -> `medlog-clients` -> `Client Scopes`.
   - Click on the `medlog-clients-dedicated` scope.
   - Go to the "Mappers" tab. Click "Configure a new mapper" -> "User Realm Role".
   - Give it a name (e.g., "Realm Roles Mapper"), set "Token Claim Name" to `realm_access.roles`, and ensure "Add to access token" is ON. Save.

## User Flow

1. **Login**: Keycloak OIDC authentication for all users
2. **Role Selection**: Choose your role (Admin, Doctor, Pharmacist, Nurse)
3. **Ward Selection**: For role-specific users, select your ward context
4. **Role Interface**: Access the appropriate interface based on your role

## API Authentication

The backend uses Keycloak OIDC JWT authentication. Include the `Authorization: Bearer <token>` header in your requests:

```bash
curl -H "Authorization: Bearer your-jwt-token" http://localhost/api/drugs
```

Tokens are obtained from Keycloak after user authentication through the frontend application.

## Roles and Permissions

- **Pharmacist**: Can manage drug inventory and view low stock alerts
- **Doctor**: Can create medication orders (prescriptions)
- **Nurse**: Can administer medications (decrements stock automatically)

## Core Features

- **Drug Inventory Management**: Track stock levels and set low stock thresholds
- **Medication Orders**: Doctors create prescriptions for patients
- **Medication Administration**: Nurses record administrations and stock is automatically decremented
- **Role-Based Access Control**: Different permissions for different user types

## Development

- Frontend code is in `frontend-medlogistics/`
- Backend code is in `backend/`
- Database is SQLite for simplicity (stored in Docker volume)

## API Endpoints

- `GET /api/drugs` - View all drugs (authenticated users)
- `POST /api/drugs` - Create drug (pharmacist only)
- `PUT /api/drugs/{id}` - Update drug (pharmacist only)
- `GET /api/drugs/low-stock` - View low stock drugs (pharmacist only)
- `GET /api/orders` - View active orders (authenticated users)
- `POST /api/orders` - Create order (doctor only)
- `POST /api/administrations` - Record administration (nurse only) 