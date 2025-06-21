# ValMed Technical Documentation

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Angular)     │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│   Port: 4200    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Traefik       │    │   Airflow       │    │   Blockchain    │
│   (Reverse      │    │   (Data         │    │   (Ganache)     │
│    Proxy)       │    │    Pipeline)    │    │   Port: 8545    │
│   Port: 80      │    │   Port: 8080    │    └─────────────────┘
└─────────────────┘    └─────────────────┘
```

### Component Details

#### Backend (FastAPI)
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **Database ORM**: SQLAlchemy 2.0+
- **Authentication**: JWT with PyJWT
- **Validation**: Pydantic 2.0+
- **Documentation**: Auto-generated OpenAPI/Swagger

#### Frontend (Angular)
- **Framework**: Angular 17+
- **Language**: TypeScript 5.0+
- **UI Framework**: Bootstrap 5+
- **Charts**: Chart.js
- **HTTP Client**: Angular HttpClient

#### Database (PostgreSQL)
- **Version**: PostgreSQL 15+
- **Connection Pooling**: SQLAlchemy
- **Migrations**: Alembic (planned)

#### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Traefik 2.11+
- **Data Pipeline**: Apache Airflow 2.8+
- **Blockchain**: Ganache (Ethereum local)

## 📊 Database Schema

### Entity Relationship Diagram

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patients table
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(50) NOT NULL,
    contact_info TEXT,
    diagnosis TEXT,
    blockchain_record_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Drugs table
CREATE TABLE drugs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(255),
    price_per_unit DECIMAL(10,2) NOT NULL,
    effectiveness_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prescriptions table
CREATE TABLE prescriptions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    drug_id INTEGER REFERENCES drugs(id),
    prescription_date TIMESTAMP,
    dosage VARCHAR(255),
    duration VARCHAR(255),
    cost_at_time_of_prescription DECIMAL(10,2),
    effectiveness_at_time_of_prescription DECIMAL(3,2),
    calculated_icer DECIMAL(10,2),
    qaly_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analyses table
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    type VARCHAR(255) NOT NULL,
    input_data TEXT NOT NULL,
    result TEXT,
    user_id INTEGER REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports table
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

```sql
-- Performance indexes
CREATE INDEX idx_patients_name ON patients(name);
CREATE INDEX idx_prescriptions_patient_id ON prescriptions(patient_id);
CREATE INDEX idx_prescriptions_drug_id ON prescriptions(drug_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_analyses_user_id ON analyses(user_id);
CREATE INDEX idx_analyses_timestamp ON analyses(timestamp);
```

## 🔐 Security Implementation

### Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant Backend
    participant Database
    
    Client->>Backend: POST /token (username, password)
    Backend->>Database: Query user by email
    Database-->>Backend: User data
    Backend->>Backend: Verify password hash
    Backend-->>Client: JWT access token
    
    Note over Client,Backend: Subsequent requests
    Client->>Backend: Request with Authorization header
    Backend->>Backend: Verify JWT token
    Backend->>Backend: Check user permissions
    Backend-->>Client: Response
```

### JWT Token Structure

```json
{
  "sub": "user@example.com",
  "exp": 1640995200,
  "iat": 1640908800,
  "role": "doctor"
}
```

### Role-Based Access Control

| Role | Permissions |
|------|-------------|
| **Doctor** | Patient CRUD, Prescription CRUD, View Analytics |
| **Nurse** | Patient Read, Prescription Read |
| **Analyst** | Drug CRUD, Analytics, Reports, Data Export |
| **Admin** | All permissions, User management, Audit logs |

### Security Headers

```python
# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

## 🔄 API Design Patterns

### RESTful Endpoints

All endpoints follow REST conventions:

- **GET** /resource - List resources
- **GET** /resource/{id} - Get specific resource
- **POST** /resource - Create resource
- **PUT** /resource/{id} - Update resource
- **DELETE** /resource/{id} - Delete resource

### Response Format

```json
{
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  },
  "message": "Success",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Handling

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 📈 Analytics Implementation

### ICER Calculation

```python
def calculate_icer(cost_difference: float, effectiveness_difference: float) -> float:
    """
    Calculate Incremental Cost-Effectiveness Ratio
    
    ICER = (Cost_A - Cost_B) / (Effectiveness_A - Effectiveness_B)
    
    Args:
        cost_difference: Difference in costs between interventions
        effectiveness_difference: Difference in effectiveness between interventions
        
    Returns:
        float: ICER value
    """
    if effectiveness_difference == 0:
        return float('inf')
    return cost_difference / effectiveness_difference
```

### QALY Calculation

```python
def calculate_qaly(utility_score: float, time_period: float) -> float:
    """
    Calculate Quality-Adjusted Life Years
    
    QALY = Utility Score × Time Period
    
    Args:
        utility_score: Health utility score (0-1)
        time_period: Time period in years
        
    Returns:
        float: QALY value
    """
    return utility_score * time_period
```

### Dashboard Metrics

```python
def get_dashboard_metrics(db: Session) -> dict:
    """Calculate real-time dashboard metrics"""
    return {
        "total_patients": db.query(models.Patient).count(),
        "total_prescriptions": db.query(models.Prescription).count(),
        "total_drugs": db.query(models.Drug).count(),
        "average_icer": calculate_average_icer(db),
        "cost_trends": get_cost_trends(db),
        "effectiveness_trends": get_effectiveness_trends(db)
    }
```

## 🔗 Blockchain Integration

### Patient Record Hashing

```python
def hash_patient_data(patient_data: dict) -> str:
    """
    Create SHA-256 hash of patient data for blockchain storage
    
    Args:
        patient_data: Patient information dictionary
        
    Returns:
        str: Hexadecimal hash string
    """
    import hashlib
    import json
    
    # Sort keys for consistent hashing
    sorted_data = json.dumps(patient_data, sort_keys=True)
    return hashlib.sha256(sorted_data.encode()).hexdigest()
```

### Blockchain Contract Interface

```python
class BlockchainManager:
    """Manages blockchain interactions for data integrity"""
    
    def __init__(self, contract_address: str, web3_provider: str):
        self.web3 = Web3(Web3.HTTPProvider(web3_provider))
        self.contract = self.web3.eth.contract(
            address=contract_address,
            abi=CONTRACT_ABI
        )
    
    def store_record_hash(self, patient_id: int, data_hash: str) -> bool:
        """Store patient record hash on blockchain"""
        try:
            tx = self.contract.functions.storeHash(patient_id, data_hash).transact()
            return self.web3.eth.wait_for_transaction_receipt(tx)
        except Exception as e:
            logger.error(f"Blockchain storage failed: {e}")
            return False
    
    def verify_record_hash(self, patient_id: int, data_hash: str) -> bool:
        """Verify patient record hash on blockchain"""
        try:
            stored_hash = self.contract.functions.getHash(patient_id).call()
            return stored_hash == data_hash
        except Exception as e:
            logger.error(f"Blockchain verification failed: {e}")
            return False
```

## 🧪 Testing Strategy

### Backend Testing

```python
# Unit tests for CRUD operations
def test_create_patient():
    """Test patient creation with valid data"""
    patient_data = {
        "name": "John Doe",
        "date_of_birth": "1990-01-01",
        "gender": "Male"
    }
    
    patient = crud.create_patient(db, patient_data)
    assert patient.name == "John Doe"
    assert patient.id is not None

# Integration tests for API endpoints
def test_patient_endpoints():
    """Test complete patient CRUD workflow"""
    # Create patient
    response = client.post("/patients/", json=patient_data)
    assert response.status_code == 200
    
    # Get patient
    patient_id = response.json()["id"]
    response = client.get(f"/patients/{patient_id}")
    assert response.status_code == 200
    
    # Update patient
    update_data = {"name": "Jane Doe"}
    response = client.put(f"/patients/{patient_id}", json=update_data)
    assert response.status_code == 200
    
    # Delete patient
    response = client.delete(f"/patients/{patient_id}")
    assert response.status_code == 200
```

### Frontend Testing

```typescript
// Component testing
describe('PatientListComponent', () => {
  it('should display patients', () => {
    const fixture = TestBed.createComponent(PatientListComponent);
    const component = fixture.componentInstance;
    
    component.patients = [
      { id: 1, name: 'John Doe', date_of_birth: '1990-01-01' }
    ];
    
    fixture.detectChanges();
    const compiled = fixture.nativeElement;
    expect(compiled.textContent).toContain('John Doe');
  });
});

// Service testing
describe('PatientService', () => {
  it('should fetch patients', (done) => {
    service.getPatients().subscribe(patients => {
      expect(patients.length).toBeGreaterThan(0);
      done();
    });
  });
});
```

## 🚀 Performance Optimization

### Database Optimization

```python
# Query optimization with eager loading
def get_patients_with_prescriptions(db: Session):
    """Get patients with their prescriptions using eager loading"""
    return db.query(models.Patient).options(
        joinedload(models.Patient.prescriptions)
    ).all()

# Pagination for large datasets
def get_patients_paginated(db: Session, skip: int = 0, limit: int = 100):
    """Get patients with pagination"""
    return db.query(models.Patient).offset(skip).limit(limit).all()
```

### Caching Strategy

```python
# Redis caching for frequently accessed data
from redis import Redis
import json

redis_client = Redis(host='localhost', port=6379, db=0)

def get_cached_metrics():
    """Get dashboard metrics from cache or calculate"""
    cache_key = "dashboard_metrics"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    metrics = calculate_dashboard_metrics()
    redis_client.setex(cache_key, 300, json.dumps(metrics))  # 5 min cache
    return metrics
```

### Frontend Optimization

```typescript
// Lazy loading for Angular modules
const routes: Routes = [
  {
    path: 'patients',
    loadChildren: () => import('./patients/patients.module').then(m => m.PatientsModule)
  }
];

// Virtual scrolling for large lists
@Component({
  selector: 'app-patient-list',
  template: `
    <cdk-virtual-scroll-viewport itemSize="50" class="viewport">
      <div *cdkVirtualFor="let patient of patients">
        {{ patient.name }}
      </div>
    </cdk-virtual-scroll-viewport>
  `
})
```

## 📊 Monitoring & Logging

### Application Logging

```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('valmed.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Structured logging
def log_user_action(user_id: int, action: str, details: dict):
    """Log user actions for audit purposes"""
    logger.info(
        "User action",
        extra={
            "user_id": user_id,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### Health Checks

```python
@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": check_database_connection(),
        "blockchain": check_blockchain_connection()
    }
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Collect metrics for all HTTP requests"""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)
    
    return response

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")
```

## 🔄 Deployment Pipeline

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy ValMed

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
      - name: Run frontend tests
        run: |
          cd frontend
          npm install
          npm test

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker images
        run: |
          docker-compose build
      - name: Push to registry
        run: |
          docker push valmed/backend:latest
          docker push valmed/frontend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          ssh user@server "cd /opt/valmed && docker-compose pull && docker-compose up -d"
```

### Environment Configuration

```bash
# Production environment variables
export DATABASE_URL="postgresql://user:pass@prod-db:5432/valmed"
export SECRET_KEY="your-super-secret-production-key"
export DEBUG="False"
export LOG_LEVEL="INFO"
export REDIS_URL="redis://prod-redis:6379"
export BLOCKCHAIN_RPC="https://mainnet.infura.io/v3/your-project-id"
```

## 📚 API Documentation

### OpenAPI Specification

The API documentation is automatically generated from the FastAPI application and available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Example API Usage

```bash
# Authentication
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=doctor@example.com&password=password123"

# Create patient
curl -X POST "http://localhost:8000/patients/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "date_of_birth": "1990-01-01",
    "gender": "Male"
  }'

# Get dashboard metrics
curl -X GET "http://localhost:8000/dashboard/metrics" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

This technical documentation provides comprehensive information for developers working on the ValMed platform. For additional support, refer to the main README.md or contact the development team. 