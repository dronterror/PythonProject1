# ValMed Healthcare Analytics Platform

A comprehensive healthcare analytics platform for patient management, drug analysis, cost-effectiveness studies, and blockchain-based data integrity.

## 🏥 Overview

ValMed is a full-stack healthcare analytics platform that provides:

- **Patient Management**: Complete CRUD operations for patient records
- **Drug Management**: Drug catalog with pricing and effectiveness data
- **Prescription Management**: Prescription tracking with cost analysis
- **Analytics Dashboard**: Real-time metrics and cost-effectiveness analysis
- **Report Generation**: Automated report creation and data export
- **Audit Logging**: Comprehensive activity tracking for compliance
- **Blockchain Integration**: Data integrity and access control
- **Role-Based Access Control**: Secure multi-user environment

## 🏗️ Architecture

```
ValMed/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main API application
│   ├── models.py           # SQLAlchemy database models
│   ├── schemas.py          # Pydantic validation schemas
│   ├── crud.py             # Database operations
│   ├── auth.py             # Authentication & authorization
│   ├── blockchain.py       # Blockchain integration
│   └── database.py         # Database configuration
├── frontend/               # Angular frontend
│   ├── src/app/           # Angular components
│   ├── src/styles.css     # Global styles
│   └── angular.json       # Angular configuration
├── airflow/               # Data pipeline orchestration
│   └── dags/              # Airflow DAGs
└── docker-compose.yml     # Container orchestration
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ValMed
```

### 2. Start the Application

```bash
# Start all services
docker-compose -f docker-compose.simple.yml up --build

# Or start specific services
docker-compose -f docker-compose.simple.yml up db backend frontend --build
```

### 3. Access the Application

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Traefik Dashboard**: http://localhost:8081

## 📊 Features

### Core Functionality

#### Patient Management
- Create, read, update, delete patient records
- Patient demographics and medical history
- Blockchain-based data integrity
- Audit logging for all operations

#### Drug Management
- Drug catalog with manufacturer information
- Pricing data for cost analysis
- Effectiveness scoring
- Price validation and alerts

#### Prescription Management
- Prescription creation and tracking
- Dosage and duration management
- Cost-effectiveness calculations (ICER)
- Quality-Adjusted Life Years (QALY) scoring

#### Analytics & Reporting
- Real-time dashboard metrics
- Cost-effectiveness analysis
- Trend analysis and forecasting
- Automated report generation
- Data export (CSV, JSON)

### Advanced Features

#### Role-Based Access Control
- **Doctor**: Patient and prescription management
- **Nurse**: Patient data viewing
- **Analyst**: Analytics and drug management
- **Admin**: Full system access

#### Blockchain Integration
- Patient record hashing
- Data integrity verification
- Access control management
- Audit trail on blockchain

#### Audit Logging
- Comprehensive activity tracking
- User action logging
- IP address and user agent tracking
- Compliance-ready audit trails

## 🔧 API Endpoints

### Authentication
- `POST /token` - User login
- `POST /register` - User registration

### Patients
- `GET /patients` - List all patients
- `POST /patients/` - Create patient
- `GET /patients/{id}` - Get patient details
- `PUT /patients/{id}` - Update patient
- `DELETE /patients/{id}` - Delete patient

### Drugs
- `GET /drugs` - List all drugs
- `POST /drugs/` - Create drug
- `GET /drugs/{id}` - Get drug details
- `PUT /drugs/{id}` - Update drug
- `DELETE /drugs/{id}` - Delete drug

### Prescriptions
- `GET /prescriptions` - List all prescriptions
- `POST /prescriptions/` - Create prescription
- `GET /prescriptions/{id}` - Get prescription details
- `PUT /prescriptions/{id}` - Update prescription
- `DELETE /prescriptions/{id}` - Delete prescription

### Analytics
- `GET /dashboard/metrics` - Dashboard metrics
- `GET /dashboard/trends` - Trend analysis
- `GET /metrics/icer` - ICER calculations
- `GET /metrics/qaly` - QALY metrics

### Reports & Export
- `POST /reports/generate/patient-summary` - Patient summary report
- `POST /reports/generate/drug-performance` - Drug performance report
- `GET /export/patients/csv` - Export patients to CSV
- `GET /export/all/json` - Export all data to JSON

### Audit Logs
- `GET /audit-logs/` - View audit logs
- `GET /audit-logs/my-activity` - Personal activity log

## 🛠️ Development

### Backend Development

The backend is built with FastAPI and includes:

- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation
- **JWT**: Authentication
- **PostgreSQL**: Database

#### Key Files:
- `main.py`: Main application with all endpoints
- `models.py`: Database models
- `schemas.py`: Pydantic validation schemas
- `crud.py`: Database operations
- `auth.py`: Authentication and authorization

### Frontend Development

The frontend is built with Angular and includes:

- **Angular 17**: Modern frontend framework
- **TypeScript**: Type-safe JavaScript
- **Bootstrap**: UI components
- **Chart.js**: Data visualization

#### Key Components:
- Dashboard: Real-time metrics and charts
- Patients: Patient management interface
- Drugs: Drug catalog management
- Prescriptions: Prescription tracking
- Reports: Report generation and viewing
- Audit Logs: Activity monitoring

### Database Schema

The application uses PostgreSQL with the following main tables:

- **users**: User accounts and roles
- **patients**: Patient information
- **drugs**: Drug catalog
- **prescriptions**: Prescription records
- **analyses**: Analysis results
- **audit_logs**: Activity tracking
- **reports**: Generated reports

## 🔒 Security

### Authentication
- JWT-based authentication
- Password hashing with bcrypt
- Token expiration and refresh

### Authorization
- Role-based access control
- Endpoint-level permissions
- User activity monitoring

### Data Protection
- Input validation with Pydantic
- SQL injection prevention
- XSS protection
- CORS configuration

## 📈 Analytics & Metrics

### Cost-Effectiveness Analysis
- **ICER (Incremental Cost-Effectiveness Ratio)**: Cost per unit of effectiveness
- **QALY (Quality-Adjusted Life Years)**: Health outcome measurement
- **Cost Analysis**: Drug pricing and prescription costs

### Dashboard Metrics
- Patient count and demographics
- Drug utilization and costs
- Prescription trends
- Cost-effectiveness ratios

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Set environment variables
   export DATABASE_URL="postgresql://user:pass@host:5432/valmed"
   export SECRET_KEY="your-secret-key"
   ```

2. **Database Migration**
   ```bash
   # Run database migrations
   alembic upgrade head
   ```

3. **Build and Deploy**
   ```bash
   # Build production images
   docker-compose -f docker-compose.yml build
   
   # Deploy
   docker-compose -f docker-compose.yml up -d
   ```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://valmed:valmedpass@db:5432/valmed` |
| `SECRET_KEY` | JWT secret key | `supersecret` |
| `DEBUG` | Debug mode | `False` |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Add comprehensive comments
- Write unit tests
- Update documentation

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs`

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Added analytics dashboard
- **v1.2.0**: Added blockchain integration
- **v1.3.0**: Enhanced reporting and export features

---

**ValMed Healthcare Analytics Platform** - Empowering healthcare decisions through data-driven insights. 