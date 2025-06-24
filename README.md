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

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd ValMed
   ```

2. **Create environment file**:
   ```bash
   cp backend/.env.example backend/.env
   ```

3. **Add hosts entries** (Windows: edit `C:\Windows\System32\drivers\etc\hosts`):
   ```
   127.0.0.1 medlog.local api.medlog.local
   ```

4. **Build and run**:
   ```bash
   docker-compose up --build
   ```

5. **Access the application**:
   - Frontend: http://medlog.local (unified interface for all roles)
   - Backend API: http://api.medlog.local
   - Traefik Dashboard: http://localhost:8080

## User Flow

1. **Login**: Auth0 authentication for all users
2. **Role Selection**: Choose your role (Admin, Doctor, Pharmacist, Nurse)
3. **Ward Selection**: For role-specific users, select your ward context
4. **Role Interface**: Access the appropriate interface based on your role

## API Authentication

The backend uses API key authentication. Include the `X-API-Key` header in your requests:

```bash
curl -H "X-API-Key: your-api-key" http://api.localhost/api/drugs
```

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