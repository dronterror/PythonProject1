# Medication Logistics MVP - ValMed Platform

## Overview

The Medication Logistics MVP is a subservice integrated into the existing ValMed ICER platform. It implements a "Restaurant Model" for hospital medication management, treating medication as orders that flow from prescription to administration to inventory deduction.

## Core Concept: The Restaurant Model

- **The Menu**: Hospital's approved drug formulary
- **The Waiter**: Doctor who places medication orders (prescriptions)
- **The Kitchen Display**: Nurse's real-time task list (Medication Administration Record)
- **The Pantry**: Hospital pharmacy inventory

## System Architecture

### Backend (FastAPI)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based with role-based access control
- **API**: RESTful endpoints for medication logistics operations

### Frontend (React)
- **Desktop Interface**: For pharmacists and doctors
- **Mobile-First PWA**: For nurses (tablet-optimized)
- **Responsive Design**: Works across all device sizes

## Key Features

### 1. Pharmacy Module (Formulary Management)
- **Location**: `/medication/formulary`
- **Users**: Pharmacists
- **Features**:
  - Add/edit/delete drugs in formulary
  - Set current stock levels
  - Configure low stock thresholds
  - Visual alerts for low stock items

### 2. Prescription Module (Doctor Interface)
- **Location**: `/medication/prescriptions`
- **Users**: Doctors
- **Features**:
  - View ward patients
  - Create medication orders
  - Select drugs from formulary
  - Set dosage and schedule

### 3. Nurse Module (Mobile PWA)
- **Location**: `/medication/nurse`
- **Users**: Nurses
- **Features**:
  - Real-time task dashboard
  - Patient medication lists
  - One-tap administration recording
  - Status tracking (Due, Completed, Missed)

### 4. Pharmacy Alerts (Inventory Management)
- **Location**: `/medication/alerts`
- **Users**: Pharmacists
- **Features**:
  - Low stock alerts
  - Stock level updates
  - Severity-based prioritization

## Critical Business Logic

### Atomic Administration Transaction
When a nurse taps "Administer":
1. Creates administration record
2. Decrements drug stock by 1 unit
3. Both operations happen in a single database transaction
4. If either fails, both are rolled back

## API Endpoints

### Medication Drugs
- `GET /medication/drugs` - List all drugs
- `POST /medication/drugs/` - Create new drug
- `PUT /medication/drugs/{id}` - Update drug
- `DELETE /medication/drugs/{id}` - Delete drug

### Medication Orders
- `GET /medication/orders` - List all orders
- `POST /medication/orders/` - Create new order
- `PUT /medication/orders/{id}` - Update order
- `DELETE /medication/orders/{id}` - Delete order

### Medication Administrations
- `POST /medication/administrations/` - Record administration
- `GET /medication/administrations` - List administrations

### Dashboard Endpoints
- `GET /medication/ward/patients` - Ward patient list
- `GET /medication/nurse/tasks` - Nurse task list
- `GET /medication/pharmacy/alerts` - Low stock alerts

## User Roles & Permissions

### Pharmacist
- Manage drug formulary
- View and update stock levels
- Access pharmacy alerts
- Full CRUD on medication drugs

### Doctor
- Create medication orders
- View patient lists
- Manage prescriptions
- Cannot access inventory management

### Nurse
- View medication tasks
- Record administrations
- Access patient-specific medication lists
- Cannot modify orders or inventory

## Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
# Set up environment variables
export DATABASE_URL="postgresql://user:password@localhost/valmed"
export SECRET_KEY="your-secret-key"
# Run migrations
python -c "from database import engine; from models import Base; Base.metadata.create_all(engine)"
# Start server
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend-react
npm install
# Set API URL
export REACT_APP_API_URL="http://localhost:8000"
# Start development server
npm start
```

## Testing the System

### Sample Workflow
1. **Pharmacist**: Add drugs to formulary with stock levels
2. **Doctor**: Create medication orders for patients
3. **Nurse**: View tasks and record administrations
4. **System**: Automatically deducts stock and updates status

### Test Data
The system includes development endpoints for testing without authentication:
- `/dev/medication/drugs/` - Create test drugs
- `/dev/medication/orders/` - Create test orders

## Security Considerations

- JWT-based authentication
- Role-based access control
- Input validation and sanitization
- SQL injection prevention via SQLAlchemy
- CORS configuration for frontend access

## Performance Optimizations

- Database connection pooling
- Response caching for static data
- Efficient queries with proper indexing
- Frontend code splitting and lazy loading

## Troubleshooting

### Common Issues
1. **CORS Errors**: Ensure backend CORS settings include frontend URL
2. **Database Connection**: Verify PostgreSQL is running and accessible
3. **Authentication**: Check JWT token validity and user roles
4. **Stock Deduction**: Verify atomic transaction is working correctly

### Logs
- Backend logs: Check FastAPI application logs
- Frontend logs: Browser developer console
- Database logs: PostgreSQL logs for transaction issues 