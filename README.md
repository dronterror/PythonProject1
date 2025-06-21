# ValMed - Medication Logistics MVP

A simplified medication logistics platform with one frontend (React PWA) and one backend (FastAPI).

## Architecture

- **Frontend**: React PWA with Vite, Tailwind CSS, and Workbox
- **Backend**: FastAPI with SQLite, API key authentication, and RBAC
- **Reverse Proxy**: Traefik for routing and load balancing
- **Containerization**: Docker Compose for easy deployment

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
   127.0.0.1 localhost
   ```

4. **Build and run**:
   ```bash
   docker-compose up --build
   ```

5. **Access the application**:
   - Frontend: http://localhost
   - Backend API: http://api.localhost
   - Traefik Dashboard: http://localhost:8080

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