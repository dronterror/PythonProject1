"""
ValMed Healthcare Analytics Platform - Main FastAPI Application

This module contains the main FastAPI application with all API endpoints for:
- User authentication and authorization
- Patient management (CRUD operations)
- Drug management (CRUD operations) 
- Prescription management (CRUD operations)
- Analysis management (CRUD operations)
- Dashboard metrics and analytics
- Report generation and data export
- Audit logging
- Blockchain integration for data integrity

Author: ValMed Development Team
Version: 1.0.0
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
import models, schemas, crud, auth, blockchain
from database import engine, Base, SessionLocal
from datetime import timedelta, datetime
from typing import List
import uvicorn
import csv
import io
import json
import time
from functools import lru_cache

# Initialize FastAPI application with performance optimizations
app = FastAPI(
    title="ValMed Healthcare Analytics API",
    description="Comprehensive healthcare analytics platform for patient management, drug analysis, and cost-effectiveness studies",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add performance middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Gzip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add trusted host middleware for security
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Create database tables on startup
Base.metadata.create_all(bind=engine)

# Database dependency with connection pooling optimization
def get_db():
    """Database dependency that provides a database session to API endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Response caching decorator
def cache_response(ttl_seconds: int = 300):
    """Cache decorator for API responses"""
    def decorator(func):
        cache = {}
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Check if cached response exists and is still valid
            if cache_key in cache:
                cached_time, cached_response = cache[cache_key]
                if time.time() - cached_time < ttl_seconds:
                    return cached_response
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = (time.time(), result)
            return result
        return wrapper
    return decorator

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT access token
    
    Args:
        form_data: OAuth2 password form containing username and password
        db: Database session
        
    Returns:
        dict: Access token and token type
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not crud.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account
    
    Args:
        user: User creation data (email, password, role)
        db: Database session
        
    Returns:
        UserOut: Created user information
        
    Raises:
        HTTPException: If email is already registered
    """
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

# ============================================================================
# PATIENT MANAGEMENT ENDPOINTS (CRUD Operations)
# ============================================================================

@app.post("/patients/", response_model=schemas.PatientOut)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    """
    Create a new patient record with audit logging
    
    Args:
        patient: Patient creation data
        db: Database session
        user: Authenticated doctor user
        
    Returns:
        PatientOut: Created patient information
    """
    return crud.create_patient_with_audit(db=db, patient=patient, user_id=user.id)

@app.get("/patients", response_model=List[schemas.PatientOut])
def get_patients(db: Session = Depends(get_db)):
    """
    Retrieve all patients
    
    Args:
        db: Database session
        
    Returns:
        List[PatientOut]: List of all patients
    """
    return crud.get_patients(db)

@app.get("/patients/{patient_id}", response_model=schemas.PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific patient by ID
    
    Args:
        patient_id: Patient ID
        db: Database session
        
    Returns:
        PatientOut: Patient information
        
    Raises:
        HTTPException: If patient not found
    """
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.put("/patients/{patient_id}", response_model=schemas.PatientOut)
def update_patient(patient_id: int, patient: schemas.PatientUpdate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    """
    Update a patient record with audit logging
    
    Args:
        patient_id: Patient ID
        patient: Patient update data
        db: Database session
        user: Authenticated doctor user
        
    Returns:
        PatientOut: Updated patient information
        
    Raises:
        HTTPException: If patient not found
    """
    db_patient = crud.update_patient_with_audit(db=db, patient_id=patient_id, patient=patient, user_id=user.id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    """
    Delete a patient record with audit logging
    
    Args:
        patient_id: Patient ID
        db: Database session
        user: Authenticated doctor user
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If patient not found
    """
    success = crud.delete_patient_with_audit(db=db, patient_id=patient_id, user_id=user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}

# Drugs - Full CRUD
@app.post("/drugs/", response_model=schemas.DrugOut)
def create_drug(drug: schemas.DrugCreate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Create a new drug with audit logging"""
    return crud.create_drug_with_audit(db=db, drug=drug, user_id=user.id)

@app.get("/drugs", response_model=List[schemas.DrugOut])
def get_drugs(db: Session = Depends(get_db)):
    """
    Retrieve all drugs
    
    Args:
        db: Database session
        
    Returns:
        List[DrugOut]: List of all drugs
    """
    return crud.get_drugs(db)

@app.get("/drugs/{drug_id}", response_model=schemas.DrugOut)
def get_drug(drug_id: int, db: Session = Depends(get_db)):
    drug = crud.get_drug(db, drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    return drug

@app.put("/drugs/{drug_id}", response_model=schemas.DrugOut)
def update_drug(drug_id: int, drug: schemas.DrugUpdate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Update a drug with audit logging"""
    db_drug = crud.update_drug_with_audit(db=db, drug_id=drug_id, drug=drug, user_id=user.id)
    if db_drug is None:
        raise HTTPException(status_code=404, detail="Drug not found")
    return db_drug

@app.delete("/drugs/{drug_id}")
def delete_drug(drug_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Delete a drug with audit logging"""
    success = crud.delete_drug_with_audit(db=db, drug_id=drug_id, user_id=user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Drug not found")
    return {"message": "Drug deleted successfully"}

# Prescriptions - Full CRUD
@app.post("/prescriptions/", response_model=schemas.PrescriptionOut)
def create_prescription(prescription: schemas.PrescriptionCreate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    """Create a new prescription with audit logging"""
    return crud.create_prescription_with_audit(db=db, prescription=prescription, user_id=user.id)

@app.get("/prescriptions", response_model=List[schemas.PrescriptionOut])
def get_prescriptions(db: Session = Depends(get_db)):
    """
    Retrieve all prescriptions
    
    Args:
        db: Database session
        
    Returns:
        List[PrescriptionOut]: List of all prescriptions
    """
    return crud.get_prescriptions(db)

@app.get("/prescriptions/{prescription_id}", response_model=schemas.PrescriptionOut)
def get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = crud.get_prescription(db, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

@app.put("/prescriptions/{prescription_id}", response_model=schemas.PrescriptionOut)
def update_prescription(prescription_id: int, prescription: schemas.PrescriptionUpdate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    """Update a prescription with audit logging"""
    db_prescription = crud.update_prescription_with_audit(db=db, prescription_id=prescription_id, prescription=prescription, user_id=user.id)
    if db_prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return db_prescription

@app.delete("/prescriptions/{prescription_id}")
def delete_prescription(prescription_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    """Delete a prescription with audit logging"""
    success = crud.delete_prescription_with_audit(db=db, prescription_id=prescription_id, user_id=user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return {"message": "Prescription deleted successfully"}

# Analyses - Full CRUD
@app.post("/analyses/", response_model=schemas.AnalysisOut)
def create_analysis(analysis: schemas.AnalysisCreate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Create a new analysis with audit logging"""
    return crud.create_analysis_with_audit(db=db, analysis=analysis, user_id=user.id)

@app.get("/analyses", response_model=List[schemas.AnalysisOut])
def get_analyses(db: Session = Depends(get_db)):
    """
    Retrieve all analyses
    
    Args:
        db: Database session
        
    Returns:
        List[AnalysisOut]: List of all analyses
    """
    return crud.get_analyses(db)

@app.get("/analyses/{analysis_id}", response_model=schemas.AnalysisOut)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = crud.get_analysis(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@app.put("/analyses/{analysis_id}", response_model=schemas.AnalysisOut)
def update_analysis(analysis_id: int, analysis: schemas.AnalysisUpdate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Update an analysis with audit logging"""
    db_analysis = crud.update_analysis_with_audit(db=db, analysis_id=analysis_id, analysis=analysis, user_id=user.id)
    if db_analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return db_analysis

@app.delete("/analyses/{analysis_id}")
def delete_analysis(analysis_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Delete an analysis with audit logging"""
    success = crud.delete_analysis_with_audit(db=db, analysis_id=analysis_id, user_id=user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"message": "Analysis deleted successfully"}

# ICER calculation endpoint (for dashboard)
@app.get("/metrics/icer")
def get_icer(db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    prescriptions = crud.get_prescriptions(db)
    if not prescriptions:
        return {"icer": None}
    # Simple ICER calculation: average of all
    costs = [p.cost_at_time_of_prescription for p in prescriptions if p.cost_at_time_of_prescription and p.effectiveness_at_time_of_prescription]
    effects = [p.effectiveness_at_time_of_prescription for p in prescriptions if p.cost_at_time_of_prescription and p.effectiveness_at_time_of_prescription]
    if not costs or not effects or sum(effects) == 0:
        return {"icer": None}
    delta_cost = sum(costs)
    delta_effect = sum(effects)
    icer = delta_cost / delta_effect if delta_effect else None
    return {"icer": icer}

# Blockchain PoC endpoints
@app.post("/blockchain/add-record-hash")
def add_record_hash(patient_id: int, data_hash: str, user: models.User = Depends(auth.get_current_active_user)):
    return blockchain.add_record_hash(patient_id, data_hash)

@app.get("/blockchain/verify-record-hash")
def verify_record_hash(patient_id: int, index: int, user: models.User = Depends(auth.get_current_active_user)):
    return blockchain.verify_record_hash(patient_id, index)

@app.post("/blockchain/grant-access")
def grant_access(patient_id: int, recipient_address: str, user: models.User = Depends(auth.get_current_active_user)):
    return blockchain.grant_access(patient_id, recipient_address)

@app.post("/blockchain/revoke-access")
def revoke_access(patient_id: int, recipient_address: str, user: models.User = Depends(auth.get_current_active_user)):
    return blockchain.revoke_access(patient_id, recipient_address)

# Basic HTML UI
@app.get("/")
def home():
    """
    Root endpoint providing API information
    
    Returns:
        dict: API information and available endpoints
    """
    return {
        "message": "ValMed Healthcare Analytics API",
        "version": "1.0.0",
        "description": "Comprehensive healthcare analytics platform for patient management, drug analysis, and cost-effectiveness studies",
        "endpoints": {
            "authentication": "/token, /register",
            "patients": "/patients",
            "drugs": "/drugs", 
            "prescriptions": "/prescriptions",
            "analyses": "/analyses",
            "dashboard": "/dashboard/metrics, /dashboard/trends",
            "reports": "/reports",
            "audit_logs": "/audit-logs",
            "exports": "/export/*",
            "analytics": "/analytics/*"
        },
        "docs": "/docs"
    }

# Login endpoint removed - no templates available
# @app.get("/login", response_class=HTMLResponse)
# def login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

@app.get("/metrics/qaly")
def get_qaly(db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    prescriptions = crud.get_prescriptions(db)
    qaly_scores = [p.qaly_score for p in prescriptions if p.qaly_score is not None]
    if not qaly_scores:
        return {"qaly": None}
    avg_qaly = sum(qaly_scores) / len(qaly_scores)
    return {"qaly": avg_qaly}

# Report endpoints
@app.post("/reports", response_model=schemas.ReportOut)
def create_report(report: schemas.ReportCreate, db: Session = Depends(get_db)):
    return crud.create_report(db, report)

@app.get("/reports/", response_model=List[schemas.ReportOut])
def get_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Get all reports"""
    reports = crud.get_reports(db, skip=skip, limit=limit)
    return reports

@app.get("/reports/{report_id}", response_model=schemas.ReportOut)
def get_report(report_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Get a specific report"""
    report = crud.get_report(db, report_id=report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

# Audit log endpoints
@app.post("/audit-logs", response_model=schemas.AuditLogOut)
def create_audit_log(audit_log: schemas.AuditLogCreate, db: Session = Depends(get_db)):
    return crud.create_audit_log(db, audit_log)

@app.get("/audit-logs/", response_model=List[schemas.AuditLogOut])
def get_audit_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: models.User = Depends(auth.require_admin)):
    """Get all audit logs (admin only)"""
    audit_logs = crud.get_audit_logs(db, skip=skip, limit=limit)
    return audit_logs

@app.get("/audit-logs/user/{user_id}", response_model=List[schemas.AuditLogOut])
def get_audit_logs_by_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: models.User = Depends(auth.require_admin)):
    """Get audit logs for a specific user (admin only)"""
    audit_logs = crud.get_audit_logs_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return audit_logs

@app.get("/audit-logs/action/{action}", response_model=List[schemas.AuditLogOut])
def get_audit_logs_by_action(action: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: models.User = Depends(auth.require_admin)):
    """Get audit logs for a specific action (admin only)"""
    audit_logs = crud.get_audit_logs_by_action(db, action=action, skip=skip, limit=limit)
    return audit_logs

@app.get("/audit-logs/my-activity", response_model=List[schemas.AuditLogOut])
def get_my_audit_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: models.User = Depends(auth.require_authenticated)):
    """Get current user's audit logs"""
    audit_logs = crud.get_audit_logs_by_user(db, user_id=user.id, skip=skip, limit=limit)
    return audit_logs

# Development endpoints (no authentication required)
@app.get("/dev/audit-logs/", response_model=List[schemas.AuditLogOut])
def get_audit_logs_dev(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all audit logs (development version - no auth required)"""
    audit_logs = crud.get_audit_logs(db, skip=skip, limit=limit)
    return audit_logs

@app.get("/dev/audit-logs/user/{user_id}", response_model=List[schemas.AuditLogOut])
def get_audit_logs_by_user_dev(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get audit logs for a specific user (development version - no auth required)"""
    audit_logs = crud.get_audit_logs_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return audit_logs

@app.get("/dev/audit-logs/action/{action}", response_model=List[schemas.AuditLogOut])
def get_audit_logs_by_action_dev(action: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get audit logs for a specific action (development version - no auth required)"""
    audit_logs = crud.get_audit_logs_by_action(db, action=action, skip=skip, limit=limit)
    return audit_logs

@app.get("/dev/audit-logs/my-activity", response_model=List[schemas.AuditLogOut])
def get_my_audit_logs_dev(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get current user's audit logs (development version - no auth required)"""
    # For development, return all audit logs
    audit_logs = crud.get_audit_logs(db, skip=skip, limit=limit)
    return audit_logs

# Report Management Endpoints

@app.delete("/reports/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.require_admin)):
    """Delete a report (admin only)"""
    success = crud.delete_report(db, report_id=report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report deleted successfully"}

# Advanced Business Logic Endpoints

@app.post("/prescriptions/{prescription_id}/calculate-icer")
def calculate_icer_for_prescription(prescription_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Calculate ICER for a specific prescription"""
    prescription = crud.get_prescription(db, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    if not prescription.cost_at_time_of_prescription or not prescription.effectiveness_at_time_of_prescription:
        raise HTTPException(status_code=400, detail="Cost and effectiveness data required for ICER calculation")
    
    icer = prescription.cost_at_time_of_prescription / prescription.effectiveness_at_time_of_prescription
    
    # Update the prescription with calculated ICER
    update_data = {"calculated_icer": icer}
    crud.update_prescription(db, prescription_id, schemas.PrescriptionUpdate(**update_data))
    
    return {"prescription_id": prescription_id, "icer": icer}

@app.get("/analytics/patient/{patient_id}")
def get_patient_analytics(patient_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    """Get comprehensive analytics for a specific patient"""
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get all prescriptions for this patient
    prescriptions = db.query(models.Prescription).filter(models.Prescription.patient_id == patient_id).all()
    
    total_cost = sum(p.cost_at_time_of_prescription for p in prescriptions if p.cost_at_time_of_prescription)
    avg_effectiveness = sum(p.effectiveness_at_time_of_prescription for p in prescriptions if p.effectiveness_at_time_of_prescription) / len([p for p in prescriptions if p.effectiveness_at_time_of_prescription]) if prescriptions else 0
    
    return {
        "patient_id": patient_id,
        "patient_name": patient.name,
        "total_prescriptions": len(prescriptions),
        "total_cost": total_cost,
        "average_effectiveness": avg_effectiveness,
        "prescriptions": [{"id": p.id, "drug_id": p.drug_id, "cost": p.cost_at_time_of_prescription, "effectiveness": p.effectiveness_at_time_of_prescription} for p in prescriptions]
    }

@app.get("/analytics/drug/{drug_id}")
def get_drug_analytics(drug_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Get analytics for a specific drug"""
    drug = crud.get_drug(db, drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    
    # Get all prescriptions for this drug
    prescriptions = db.query(models.Prescription).filter(models.Prescription.drug_id == drug_id).all()
    
    total_prescriptions = len(prescriptions)
    total_revenue = sum(p.cost_at_time_of_prescription for p in prescriptions if p.cost_at_time_of_prescription)
    avg_effectiveness = sum(p.effectiveness_at_time_of_prescription for p in prescriptions if p.effectiveness_at_time_of_prescription) / len([p for p in prescriptions if p.effectiveness_at_time_of_prescription]) if prescriptions else 0
    
    return {
        "drug_id": drug_id,
        "drug_name": drug.name,
        "total_prescriptions": total_prescriptions,
        "total_revenue": total_revenue,
        "average_effectiveness": avg_effectiveness,
        "current_price": drug.price_per_unit
    }

@app.post("/drugs/{drug_id}/validate-price")
def validate_drug_price(drug_id: int, new_price: float, db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Validate if a new drug price is reasonable based on effectiveness"""
    drug = crud.get_drug(db, drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    
    # Get prescriptions for this drug
    prescriptions = db.query(models.Prescription).filter(models.Prescription.drug_id == drug_id).all()
    
    if not prescriptions:
        return {"valid": True, "message": "No prescription history available for validation"}
    
    # Calculate average effectiveness
    avg_effectiveness = sum(p.effectiveness_at_time_of_prescription for p in prescriptions if p.effectiveness_at_time_of_prescription) / len([p for p in prescriptions if p.effectiveness_at_time_of_prescription])
    
    # Simple validation: price should be proportional to effectiveness
    if avg_effectiveness > 0:
        price_per_effectiveness = new_price / avg_effectiveness
        is_reasonable = price_per_effectiveness <= 1000  # Threshold for reasonable price per effectiveness unit
        
        return {
            "valid": is_reasonable,
            "message": f"Price per effectiveness unit: {price_per_effectiveness:.2f}",
            "recommendation": "Price is reasonable" if is_reasonable else "Price may be too high for effectiveness"
        }
    
    return {"valid": True, "message": "Insufficient effectiveness data for validation"}

# Dashboard Metrics Endpoints

@app.get("/dashboard/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Get comprehensive dashboard metrics"""
    # Get all data
    patients = crud.get_patients(db)
    drugs = crud.get_drugs(db)
    prescriptions = crud.get_prescriptions(db)
    analyses = crud.get_analyses(db)
    
    # Calculate key metrics
    total_patients = len(patients)
    total_drugs = len(drugs)
    total_prescriptions = len(prescriptions)
    total_analyses = len(analyses)
    
    # Financial metrics
    total_revenue = sum(p.cost_at_time_of_prescription for p in prescriptions if p.cost_at_time_of_prescription)
    avg_prescription_cost = total_revenue / total_prescriptions if total_prescriptions > 0 else 0
    
    # Effectiveness metrics
    effective_prescriptions = [p for p in prescriptions if p.effectiveness_at_time_of_prescription]
    avg_effectiveness = sum(p.effectiveness_at_time_of_prescription for p in effective_prescriptions) / len(effective_prescriptions) if effective_prescriptions else 0
    
    # ICER metrics
    icer_prescriptions = [p for p in prescriptions if p.calculated_icer]
    avg_icer = sum(p.calculated_icer for p in icer_prescriptions) / len(icer_prescriptions) if icer_prescriptions else 0
    
    # Top performing drugs
    drug_performance = {}
    for prescription in prescriptions:
        drug_id = prescription.drug_id
        if drug_id not in drug_performance:
            drug_performance[drug_id] = {"prescriptions": 0, "revenue": 0, "effectiveness": []}
        drug_performance[drug_id]["prescriptions"] += 1
        if prescription.cost_at_time_of_prescription:
            drug_performance[drug_id]["revenue"] += prescription.cost_at_time_of_prescription
        if prescription.effectiveness_at_time_of_prescription:
            drug_performance[drug_id]["effectiveness"].append(prescription.effectiveness_at_time_of_prescription)
    
    # Calculate average effectiveness for each drug
    for drug_id in drug_performance:
        effectiveness_list = drug_performance[drug_id]["effectiveness"]
        drug_performance[drug_id]["avg_effectiveness"] = sum(effectiveness_list) / len(effectiveness_list) if effectiveness_list else 0
    
    # Get top 5 drugs by revenue
    top_drugs = sorted(drug_performance.items(), key=lambda x: x[1]["revenue"], reverse=True)[:5]
    
    return {
        "overview": {
            "total_patients": total_patients,
            "total_drugs": total_drugs,
            "total_prescriptions": total_prescriptions,
            "total_analyses": total_analyses
        },
        "financial": {
            "total_revenue": total_revenue,
            "average_prescription_cost": avg_prescription_cost
        },
        "effectiveness": {
            "average_effectiveness": avg_effectiveness,
            "effective_prescriptions_count": len(effective_prescriptions)
        },
        "health_economics": {
            "average_icer": avg_icer,
            "prescriptions_with_icer": len(icer_prescriptions)
        },
        "top_drugs": [
            {
                "drug_id": drug_id,
                "prescriptions": data["prescriptions"],
                "revenue": data["revenue"],
                "avg_effectiveness": data["avg_effectiveness"]
            }
            for drug_id, data in top_drugs
        ]
    }

@app.get("/dashboard/trends")
def get_dashboard_trends(db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Get trend data for dashboard charts"""
    prescriptions = crud.get_prescriptions(db)
    
    # Group prescriptions by month (simplified - using prescription date if available)
    monthly_data = {}
    for prescription in prescriptions:
        if prescription.prescription_date:
            month_key = prescription.prescription_date.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {"count": 0, "revenue": 0, "effectiveness": []}
            monthly_data[month_key]["count"] += 1
            if prescription.cost_at_time_of_prescription:
                monthly_data[month_key]["revenue"] += prescription.cost_at_time_of_prescription
            if prescription.effectiveness_at_time_of_prescription:
                monthly_data[month_key]["effectiveness"].append(prescription.effectiveness_at_time_of_prescription)
    
    # Calculate average effectiveness for each month
    for month in monthly_data:
        effectiveness_list = monthly_data[month]["effectiveness"]
        monthly_data[month]["avg_effectiveness"] = sum(effectiveness_list) / len(effectiveness_list) if effectiveness_list else 0
    
    return {
        "monthly_trends": [
            {
                "month": month,
                "prescriptions": data["count"],
                "revenue": data["revenue"],
                "avg_effectiveness": data["avg_effectiveness"]
            }
            for month, data in sorted(monthly_data.items())
        ]
    }

# Development endpoints - unauthenticated versions for frontend testing
@app.get("/dev/dashboard/metrics")
def get_dashboard_metrics_dev(db: Session = Depends(get_db)):
    """Get comprehensive dashboard metrics (development version - no auth required)"""
    # Get all data
    patients = crud.get_patients(db)
    drugs = crud.get_drugs(db)
    prescriptions = crud.get_prescriptions(db)
    analyses = crud.get_analyses(db)
    
    # Calculate key metrics
    total_patients = len(patients)
    total_drugs = len(drugs)
    total_prescriptions = len(prescriptions)
    total_analyses = len(analyses)
    
    # Financial metrics
    total_revenue = sum(p.cost_at_time_of_prescription for p in prescriptions if p.cost_at_time_of_prescription)
    avg_prescription_cost = total_revenue / total_prescriptions if total_prescriptions > 0 else 0
    
    # Effectiveness metrics
    effective_prescriptions = [p for p in prescriptions if p.effectiveness_at_time_of_prescription]
    avg_effectiveness = sum(p.effectiveness_at_time_of_prescription for p in effective_prescriptions) / len(effective_prescriptions) if effective_prescriptions else 0
    
    # ICER metrics
    icer_prescriptions = [p for p in prescriptions if p.calculated_icer]
    avg_icer = sum(p.calculated_icer for p in icer_prescriptions) / len(icer_prescriptions) if icer_prescriptions else 0
    
    # Top performing drugs
    drug_performance = {}
    for prescription in prescriptions:
        drug_id = prescription.drug_id
        if drug_id not in drug_performance:
            drug_performance[drug_id] = {"prescriptions": 0, "revenue": 0, "effectiveness": []}
        drug_performance[drug_id]["prescriptions"] += 1
        if prescription.cost_at_time_of_prescription:
            drug_performance[drug_id]["revenue"] += prescription.cost_at_time_of_prescription
        if prescription.effectiveness_at_time_of_prescription:
            drug_performance[drug_id]["effectiveness"].append(prescription.effectiveness_at_time_of_prescription)
    
    # Calculate average effectiveness for each drug
    for drug_id in drug_performance:
        effectiveness_list = drug_performance[drug_id]["effectiveness"]
        drug_performance[drug_id]["avg_effectiveness"] = sum(effectiveness_list) / len(effectiveness_list) if effectiveness_list else 0
    
    # Get top 5 drugs by revenue
    top_drugs = sorted(drug_performance.items(), key=lambda x: x[1]["revenue"], reverse=True)[:5]
    
    return {
        "overview": {
            "total_patients": total_patients,
            "total_drugs": total_drugs,
            "total_prescriptions": total_prescriptions,
            "total_analyses": total_analyses
        },
        "financial": {
            "total_revenue": total_revenue,
            "average_prescription_cost": avg_prescription_cost
        },
        "effectiveness": {
            "average_effectiveness": avg_effectiveness,
            "effective_prescriptions_count": len(effective_prescriptions)
        },
        "health_economics": {
            "average_icer": avg_icer,
            "prescriptions_with_icer": len(icer_prescriptions)
        },
        "top_drugs": [
            {
                "drug_id": drug_id,
                "prescriptions": data["prescriptions"],
                "revenue": data["revenue"],
                "avg_effectiveness": data["avg_effectiveness"]
            }
            for drug_id, data in top_drugs
        ]
    }

@app.get("/dev/dashboard/trends")
def get_dashboard_trends_dev(db: Session = Depends(get_db)):
    """Get trend data for dashboard charts (development version - no auth required)"""
    prescriptions = crud.get_prescriptions(db)
    
    # Group prescriptions by month (simplified - using prescription date if available)
    monthly_data = {}
    for prescription in prescriptions:
        if prescription.prescription_date:
            month_key = prescription.prescription_date.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {"count": 0, "revenue": 0, "effectiveness": []}
            monthly_data[month_key]["count"] += 1
            if prescription.cost_at_time_of_prescription:
                monthly_data[month_key]["revenue"] += prescription.cost_at_time_of_prescription
            if prescription.effectiveness_at_time_of_prescription:
                monthly_data[month_key]["effectiveness"].append(prescription.effectiveness_at_time_of_prescription)
    
    # Calculate average effectiveness for each month
    for month in monthly_data:
        effectiveness_list = monthly_data[month]["effectiveness"]
        monthly_data[month]["avg_effectiveness"] = sum(effectiveness_list) / len(effectiveness_list) if effectiveness_list else 0
    
    return {
        "monthly_trends": [
            {
                "month": month,
                "prescriptions": data["count"],
                "revenue": data["revenue"],
                "avg_effectiveness": data["avg_effectiveness"]
            }
            for month, data in sorted(monthly_data.items())
        ]
    }

# Advanced Reporting Endpoints

@app.post("/reports/generate/patient-summary")
def generate_patient_summary_report(db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    """Generate a comprehensive patient summary report"""
    patients = crud.get_patients(db)
    prescriptions = crud.get_prescriptions(db)
    
    patient_summaries = []
    for patient in patients:
        patient_prescriptions = [p for p in prescriptions if p.patient_id == patient.id]
        total_cost = sum(p.cost_at_time_of_prescription for p in patient_prescriptions if p.cost_at_time_of_prescription)
        avg_effectiveness = sum(p.effectiveness_at_time_of_prescription for p in patient_prescriptions if p.effectiveness_at_time_of_prescription) / len([p for p in patient_prescriptions if p.effectiveness_at_time_of_prescription]) if patient_prescriptions else 0
        
        patient_summaries.append({
            "patient_id": patient.id,
            "name": patient.name,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender,
            "diagnosis": patient.diagnosis,
            "total_prescriptions": len(patient_prescriptions),
            "total_cost": total_cost,
            "average_effectiveness": avg_effectiveness
        })
    
    # Save report to database
    report_content = f"Patient Summary Report - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report_content += f"Total Patients: {len(patients)}\n"
    report_content += f"Total Prescriptions: {len(prescriptions)}\n\n"
    
    for summary in patient_summaries:
        report_content += f"Patient: {summary['name']} (ID: {summary['patient_id']})\n"
        report_content += f"  Prescriptions: {summary['total_prescriptions']}\n"
        report_content += f"  Total Cost: ${summary['total_cost']:.2f}\n"
        report_content += f"  Avg Effectiveness: {summary['average_effectiveness']:.2f}\n\n"
    
    report = crud.create_report(db, schemas.ReportCreate(
        title="Patient Summary Report",
        content=report_content,
        created_by=user.id
    ))
    
    return {
        "report_id": report.id,
        "title": report.title,
        "summary": {
            "total_patients": len(patients),
            "total_prescriptions": len(prescriptions),
            "patient_summaries": patient_summaries
        }
    }

@app.post("/reports/generate/drug-performance")
def generate_drug_performance_report(db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Generate a drug performance analysis report"""
    drugs = crud.get_drugs(db)
    prescriptions = crud.get_prescriptions(db)
    
    drug_performance = []
    for drug in drugs:
        drug_prescriptions = [p for p in prescriptions if p.drug_id == drug.id]
        total_revenue = sum(p.cost_at_time_of_prescription for p in drug_prescriptions if p.cost_at_time_of_prescription)
        avg_effectiveness = sum(p.effectiveness_at_time_of_prescription for p in drug_prescriptions if p.effectiveness_at_time_of_prescription) / len([p for p in drug_prescriptions if p.effectiveness_at_time_of_prescription]) if drug_prescriptions else 0
        
        drug_performance.append({
            "drug_id": drug.id,
            "name": drug.name,
            "manufacturer": drug.manufacturer,
            "current_price": drug.price_per_unit,
            "total_prescriptions": len(drug_prescriptions),
            "total_revenue": total_revenue,
            "average_effectiveness": avg_effectiveness,
            "cost_effectiveness_ratio": total_revenue / avg_effectiveness if avg_effectiveness > 0 else 0
        })
    
    # Sort by revenue
    drug_performance.sort(key=lambda x: x["total_revenue"], reverse=True)
    
    # Save report to database
    report_content = f"Drug Performance Report - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report_content += f"Total Drugs: {len(drugs)}\n"
    report_content += f"Total Prescriptions: {len(prescriptions)}\n\n"
    
    for performance in drug_performance:
        report_content += f"Drug: {performance['name']} (ID: {performance['drug_id']})\n"
        report_content += f"  Manufacturer: {performance['manufacturer']}\n"
        report_content += f"  Current Price: ${performance['current_price']:.2f}\n"
        report_content += f"  Prescriptions: {performance['total_prescriptions']}\n"
        report_content += f"  Revenue: ${performance['total_revenue']:.2f}\n"
        report_content += f"  Avg Effectiveness: {performance['average_effectiveness']:.2f}\n"
        report_content += f"  Cost-Effectiveness Ratio: {performance['cost_effectiveness_ratio']:.2f}\n\n"
    
    report = crud.create_report(db, schemas.ReportCreate(
        title="Drug Performance Report",
        content=report_content,
        created_by=user.id
    ))
    
    return {
        "report_id": report.id,
        "title": report.title,
        "summary": {
            "total_drugs": len(drugs),
            "total_prescriptions": len(prescriptions),
            "drug_performance": drug_performance
        }
    }

@app.post("/reports/generate/financial-analysis")
def generate_financial_analysis_report(db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Generate a comprehensive financial analysis report"""
    prescriptions = crud.get_prescriptions(db)
    drugs = crud.get_drugs(db)
    
    # Financial calculations
    total_revenue = sum(p.cost_at_time_of_prescription for p in prescriptions if p.cost_at_time_of_prescription)
    avg_prescription_cost = total_revenue / len(prescriptions) if prescriptions else 0
    
    # Revenue by drug
    revenue_by_drug = {}
    for prescription in prescriptions:
        drug_id = prescription.drug_id
        if drug_id not in revenue_by_drug:
            revenue_by_drug[drug_id] = 0
        if prescription.cost_at_time_of_prescription:
            revenue_by_drug[drug_id] += prescription.cost_at_time_of_prescription
    
    # Get drug names
    drug_names = {drug.id: drug.name for drug in drugs}
    
    # Monthly revenue trends
    monthly_revenue = {}
    for prescription in prescriptions:
        if prescription.prescription_date and prescription.cost_at_time_of_prescription:
            month_key = prescription.prescription_date.strftime("%Y-%m")
            if month_key not in monthly_revenue:
                monthly_revenue[month_key] = 0
            monthly_revenue[month_key] += prescription.cost_at_time_of_prescription
    
    # Save report to database
    report_content = f"Financial Analysis Report - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report_content += f"Total Revenue: ${total_revenue:.2f}\n"
    report_content += f"Total Prescriptions: {len(prescriptions)}\n"
    report_content += f"Average Prescription Cost: ${avg_prescription_cost:.2f}\n\n"
    
    report_content += "Revenue by Drug:\n"
    for drug_id, revenue in sorted(revenue_by_drug.items(), key=lambda x: x[1], reverse=True):
        drug_name = drug_names.get(drug_id, f"Drug {drug_id}")
        report_content += f"  {drug_name}: ${revenue:.2f}\n"
    
    report_content += "\nMonthly Revenue Trends:\n"
    for month, revenue in sorted(monthly_revenue.items()):
        report_content += f"  {month}: ${revenue:.2f}\n"
    
    report = crud.create_report(db, schemas.ReportCreate(
        title="Financial Analysis Report",
        content=report_content,
        created_by=user.id
    ))
    
    return {
        "report_id": report.id,
        "title": report.title,
        "summary": {
            "total_revenue": total_revenue,
            "total_prescriptions": len(prescriptions),
            "average_prescription_cost": avg_prescription_cost,
            "revenue_by_drug": [
                {"drug_name": drug_names.get(drug_id, f"Drug {drug_id}"), "revenue": revenue}
                for drug_id, revenue in sorted(revenue_by_drug.items(), key=lambda x: x[1], reverse=True)
            ],
            "monthly_revenue": [
                {"month": month, "revenue": revenue}
                for month, revenue in sorted(monthly_revenue.items())
            ]
        }
    }

# Data Export Endpoints

@app.get("/export/patients/csv")
def export_patients_csv(db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    """Export patients data as CSV"""
    patients = crud.get_patients(db)
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'Name', 'Date of Birth', 'Gender', 'Contact Info', 'Diagnosis', 'Blockchain Record ID'])
    
    # Write data
    for patient in patients:
        writer.writerow([
            patient.id,
            patient.name,
            patient.date_of_birth,
            patient.gender,
            patient.contact_info or '',
            patient.diagnosis or '',
            patient.blockchain_record_id or ''
        ])
    
    output.seek(0)
    
    # Create audit log
    crud.create_audit_log(db, schemas.AuditLogCreate(
        action="export_patients_csv",
        user_id=user.id,
        details=f"Exported {len(patients)} patients to CSV"
    ))
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=patients.csv"}
    )

@app.get("/export/drugs/csv")
def export_drugs_csv(db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Export drugs data as CSV"""
    drugs = crud.get_drugs(db)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['ID', 'Name', 'Manufacturer', 'Price per Unit', 'Effectiveness Score'])
    
    for drug in drugs:
        writer.writerow([
            drug.id,
            drug.name,
            drug.manufacturer or '',
            drug.price_per_unit,
            drug.effectiveness_score or ''
        ])
    
    output.seek(0)
    
    # Create audit log
    crud.create_audit_log(db, schemas.AuditLogCreate(
        action="export_drugs_csv",
        user_id=user.id,
        details=f"Exported {len(drugs)} drugs to CSV"
    ))
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=drugs.csv"}
    )

@app.get("/export/prescriptions/csv")
def export_prescriptions_csv(db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    """Export prescriptions data as CSV"""
    prescriptions = crud.get_prescriptions(db)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'ID', 'Patient ID', 'Drug ID', 'Prescription Date', 'Dosage', 'Duration',
        'Cost at Time of Prescription', 'Effectiveness at Time of Prescription',
        'Calculated ICER', 'QALY Score'
    ])
    
    for prescription in prescriptions:
        writer.writerow([
            prescription.id,
            prescription.patient_id,
            prescription.drug_id,
            prescription.prescription_date or '',
            prescription.dosage or '',
            prescription.duration or '',
            prescription.cost_at_time_of_prescription or '',
            prescription.effectiveness_at_time_of_prescription or '',
            prescription.calculated_icer or '',
            prescription.qaly_score or ''
        ])
    
    output.seek(0)
    
    # Create audit log
    crud.create_audit_log(db, schemas.AuditLogCreate(
        action="export_prescriptions_csv",
        user_id=user.id,
        details=f"Exported {len(prescriptions)} prescriptions to CSV"
    ))
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=prescriptions.csv"}
    )

@app.get("/export/analyses/csv")
def export_analyses_csv(db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Export analyses data as CSV"""
    analyses = crud.get_analyses(db)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['ID', 'Type', 'Input Data', 'Result', 'User ID', 'Timestamp'])
    
    for analysis in analyses:
        writer.writerow([
            analysis.id,
            analysis.type,
            analysis.input_data,
            analysis.result or '',
            analysis.user_id or '',
            analysis.timestamp
        ])
    
    output.seek(0)
    
    # Create audit log
    crud.create_audit_log(db, schemas.AuditLogCreate(
        action="export_analyses_csv",
        user_id=user.id,
        details=f"Exported {len(analyses)} analyses to CSV"
    ))
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=analyses.csv"}
    )

@app.get("/export/all/json")
def export_all_data_json(db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    """Export all data as JSON"""
    patients = crud.get_patients(db)
    drugs = crud.get_drugs(db)
    prescriptions = crud.get_prescriptions(db)
    analyses = crud.get_analyses(db)
    
    export_data = {
        "export_date": datetime.now().isoformat(),
        "exported_by": user.email,
        "patients": [
            {
                "id": p.id,
                "name": p.name,
                "date_of_birth": p.date_of_birth.isoformat(),
                "gender": p.gender,
                "contact_info": p.contact_info,
                "diagnosis": p.diagnosis,
                "blockchain_record_id": p.blockchain_record_id
            }
            for p in patients
        ],
        "drugs": [
            {
                "id": d.id,
                "name": d.name,
                "manufacturer": d.manufacturer,
                "price_per_unit": d.price_per_unit,
                "effectiveness_score": d.effectiveness_score
            }
            for d in drugs
        ],
        "prescriptions": [
            {
                "id": p.id,
                "patient_id": p.patient_id,
                "drug_id": p.drug_id,
                "prescription_date": p.prescription_date.isoformat() if p.prescription_date else None,
                "dosage": p.dosage,
                "duration": p.duration,
                "cost_at_time_of_prescription": p.cost_at_time_of_prescription,
                "effectiveness_at_time_of_prescription": p.effectiveness_at_time_of_prescription,
                "calculated_icer": p.calculated_icer,
                "qaly_score": p.qaly_score
            }
            for p in prescriptions
        ],
        "analyses": [
            {
                "id": a.id,
                "type": a.type,
                "input_data": a.input_data,
                "result": a.result,
                "user_id": a.user_id,
                "timestamp": a.timestamp.isoformat()
            }
            for a in analyses
        ]
    }
    
    # Create audit log
    crud.create_audit_log(db, schemas.AuditLogCreate(
        action="export_all_json",
        user_id=user.id,
        details=f"Exported all data to JSON: {len(patients)} patients, {len(drugs)} drugs, {len(prescriptions)} prescriptions, {len(analyses)} analyses"
    ))
    
    return StreamingResponse(
        io.BytesIO(json.dumps(export_data, indent=2).encode('utf-8')),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=valmed_export.json"}
    )

# Development endpoints (no authentication required)
def get_or_create_dev_user(db: Session):
    """Get or create a default development user"""
    # Try to get existing dev user
    dev_user = db.query(models.User).filter(models.User.email == "dev@valmed.com").first()
    if not dev_user:
        # Create default dev user
        dev_user = models.User(
            email="dev@valmed.com",
            password_hash="dev_password_hash",  # Not used in dev mode
            role=schemas.UserRole.admin
        )
        db.add(dev_user)
        db.commit()
        db.refresh(dev_user)
    return dev_user

@app.post("/dev/patients/", response_model=schemas.PatientOut)
def create_patient_dev(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient (development version - no auth required)"""
    dev_user = get_or_create_dev_user(db)
    return crud.create_patient_with_audit(db=db, patient=patient, user_id=dev_user.id)

@app.put("/dev/patients/{patient_id}", response_model=schemas.PatientOut)
def update_patient_dev(patient_id: int, patient: schemas.PatientUpdate, db: Session = Depends(get_db)):
    """Update a patient (development version - no auth required)"""
    dev_user = get_or_create_dev_user(db)
    db_patient = crud.update_patient_with_audit(db=db, patient_id=patient_id, patient=patient, user_id=dev_user.id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@app.delete("/dev/patients/{patient_id}")
def delete_patient_dev(patient_id: int, db: Session = Depends(get_db)):
    """Delete a patient (development version - no auth required)"""
    dev_user = get_or_create_dev_user(db)
    success = crud.delete_patient_with_audit(db=db, patient_id=patient_id, user_id=dev_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}

@app.post("/dev/drugs/", response_model=schemas.DrugOut)
def create_drug_dev(drug: schemas.DrugCreate, db: Session = Depends(get_db)):
    """Create a new drug (development version - no auth required)"""
    dev_user = get_or_create_dev_user(db)
    return crud.create_drug_with_audit(db=db, drug=drug, user_id=dev_user.id)

@app.put("/dev/drugs/{drug_id}", response_model=schemas.DrugOut)
def update_drug_dev(drug_id: int, drug: schemas.DrugUpdate, db: Session = Depends(get_db)):
    """Update a drug (development version - no auth required)"""
    dev_user = get_or_create_dev_user(db)
    db_drug = crud.update_drug_with_audit(db=db, drug_id=drug_id, drug=drug, user_id=dev_user.id)
    if db_drug is None:
        raise HTTPException(status_code=404, detail="Drug not found")
    return db_drug

@app.delete("/dev/drugs/{drug_id}")
def delete_drug_dev(drug_id: int, db: Session = Depends(get_db)):
    """Delete a drug (development version - no auth required)"""
    dev_user = get_or_create_dev_user(db)
    success = crud.delete_drug_with_audit(db=db, drug_id=drug_id, user_id=dev_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Drug not found")
    return {"message": "Drug deleted successfully"}

@app.post("/dev/prescriptions/", response_model=schemas.PrescriptionOut)
def create_prescription_dev(prescription: schemas.PrescriptionCreate, db: Session = Depends(get_db)):
    """Create a new prescription (development version - no auth required)"""
    dev_user = get_or_create_dev_user(db)
    return crud.create_prescription_with_audit(db=db, prescription=prescription, user_id=dev_user.id)

@app.put("/dev/prescriptions/{prescription_id}", response_model=schemas.PrescriptionOut)
def update_prescription_dev(prescription_id: int, prescription: schemas.PrescriptionUpdate, db: Session = Depends(get_db)):
    """Update a prescription (development version - no auth required)"""
    dev_user = get_or_create_dev_user(db)
    db_prescription = crud.update_prescription_with_audit(db=db, prescription_id=prescription_id, prescription=prescription, user_id=dev_user.id)
    if db_prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return db_prescription

@app.delete("/dev/prescriptions/{prescription_id}")
def delete_prescription_dev(prescription_id: int, db: Session = Depends(get_db)):
    """Delete a prescription (development version - no auth required)"""
    dev_user = get_or_create_dev_user(db)
    success = crud.delete_prescription_with_audit(db=db, prescription_id=prescription_id, user_id=dev_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return {"message": "Prescription deleted successfully"}

@app.post("/dev/analyses/", response_model=schemas.AnalysisOut)
def create_analysis_dev(analysis: schemas.AnalysisCreate, db: Session = Depends(get_db)):
    """Create a new analysis (development version - no auth required)"""
    dev_user = get_or_create_dev_user(db)
    return crud.create_analysis_with_audit(db=db, analysis=analysis, user_id=dev_user.id)

@app.put("/dev/analyses/{analysis_id}", response_model=schemas.AnalysisOut)
def update_analysis_dev(analysis_id: int, analysis: schemas.AnalysisUpdate, db: Session = Depends(get_db)):
    """Update an analysis (development version - no auth required)"""
    dev_user = get_or_create_dev_user(db)
    db_analysis = crud.update_analysis_with_audit(db=db, analysis_id=analysis_id, analysis=analysis, user_id=dev_user.id)
    if db_analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return db_analysis

@app.delete("/dev/analyses/{analysis_id}")
def delete_analysis_dev(analysis_id: int, db: Session = Depends(get_db)):
    """Delete an analysis (development version - no auth required)"""
    dev_user = get_or_create_dev_user(db)
    success = crud.delete_analysis_with_audit(db=db, analysis_id=analysis_id, user_id=dev_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"message": "Analysis deleted successfully"}

# ============================================================================
# MEDICATION LOGISTICS API ENDPOINTS (New MVP Feature)
# ============================================================================

# Medication Drug Management (Pharmacy Module)

@app.post("/medication/drugs/", response_model=schemas.MedicationDrugOut)
def create_medication_drug(drug: schemas.MedicationDrugCreate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_pharmacist)):
    """Create a new medication drug (Pharmacy Module)"""
    return crud.create_medication_drug(db, drug)

@app.get("/medication/drugs", response_model=List[schemas.MedicationDrugOut])
def get_medication_drugs(db: Session = Depends(get_db)):
    """Get all medication drugs"""
    return crud.get_medication_drugs(db)

@app.get("/medication/drugs/{drug_id}", response_model=schemas.MedicationDrugOut)
def get_medication_drug(drug_id: int, db: Session = Depends(get_db)):
    """Get a specific medication drug"""
    drug = crud.get_medication_drug(db, drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Medication drug not found")
    return drug

@app.put("/medication/drugs/{drug_id}", response_model=schemas.MedicationDrugOut)
def update_medication_drug(drug_id: int, drug: schemas.MedicationDrugUpdate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_pharmacist)):
    """Update a medication drug (Pharmacy Module)"""
    db_drug = crud.update_medication_drug(db, drug_id, drug)
    if not db_drug:
        raise HTTPException(status_code=404, detail="Medication drug not found")
    return db_drug

@app.delete("/medication/drugs/{drug_id}")
def delete_medication_drug(drug_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.require_pharmacist)):
    """Delete a medication drug (Pharmacy Module)"""
    drug = crud.delete_medication_drug(db, drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Medication drug not found")
    return {"message": "Medication drug deleted successfully"}

# Medication Order Management (Prescription Module)

@app.post("/medication/orders/", response_model=schemas.MedicationOrderOut)
def create_medication_order(order: schemas.MedicationOrderCreate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    """Create a new medication order (Prescription Module)"""
    return crud.create_medication_order(db, order, user.id)

@app.get("/medication/orders", response_model=List[schemas.MedicationOrderOut])
def get_medication_orders(db: Session = Depends(get_db)):
    """Get all medication orders"""
    return crud.get_medication_orders(db)

@app.get("/medication/orders/{order_id}", response_model=schemas.MedicationOrderOut)
def get_medication_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific medication order"""
    order = crud.get_medication_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Medication order not found")
    return order

@app.put("/medication/orders/{order_id}", response_model=schemas.MedicationOrderOut)
def update_medication_order(order_id: int, order: schemas.MedicationOrderUpdate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    """Update a medication order (Prescription Module)"""
    db_order = crud.update_medication_order(db, order_id, order)
    if not db_order:
        raise HTTPException(status_code=404, detail="Medication order not found")
    return db_order

@app.delete("/medication/orders/{order_id}")
def delete_medication_order(order_id: int, db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    """Delete a medication order (Prescription Module)"""
    order = crud.delete_medication_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Medication order not found")
    return {"message": "Medication order deleted successfully"}

# Medication Administration (Nurse Module)

@app.post("/medication/administrations/", response_model=schemas.MedicationAdministrationOut)
def create_medication_administration(administration: schemas.MedicationAdministrationCreate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_nurse)):
    """Create a medication administration record (Nurse Module) - Critical atomic operation"""
    try:
        return crud.create_medication_administration(db, administration, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to record medication administration")

@app.get("/medication/administrations", response_model=List[schemas.MedicationAdministrationOut])
def get_medication_administrations(db: Session = Depends(get_db)):
    """Get all medication administrations"""
    return crud.get_medication_administrations(db)

@app.get("/medication/administrations/{administration_id}", response_model=schemas.MedicationAdministrationOut)
def get_medication_administration(administration_id: int, db: Session = Depends(get_db)):
    """Get a specific medication administration"""
    administration = crud.get_medication_administration(db, administration_id)
    if not administration:
        raise HTTPException(status_code=404, detail="Medication administration not found")
    return administration

# Ward and Dashboard Endpoints

@app.get("/medication/ward/patients", response_model=List[schemas.WardPatientOut])
def get_ward_patients(db: Session = Depends(get_db)):
    """Get all patients in the ward with their active medication orders"""
    return crud.get_ward_patients(db)

@app.get("/medication/nurse/tasks", response_model=List[schemas.PatientMedicationTask])
def get_nurse_tasks(db: Session = Depends(get_db), user: models.User = Depends(auth.require_nurse)):
    """Get all medication tasks for nurses (Nurse Module)"""
    return crud.get_nurse_tasks(db)

@app.get("/medication/pharmacy/alerts", response_model=List[schemas.LowStockAlert])
def get_low_stock_alerts(db: Session = Depends(get_db), user: models.User = Depends(auth.require_pharmacist)):
    """Get low stock alerts for pharmacy (Pharmacy Module)"""
    low_stock_drugs = crud.get_low_stock_medication_drugs(db)
    alerts = []
    for drug in low_stock_drugs:
        alerts.append({
            "drug": drug,
            "current_stock": drug.current_stock,
            "threshold": drug.low_stock_threshold
        })
    return alerts

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 