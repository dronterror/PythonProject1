from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext
from typing import List, Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# User CRUD

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, password_hash=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Patient CRUD

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def get_patients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Patient).offset(skip).limit(limit).all()

def get_patient(db: Session, patient_id: int):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def update_patient(db: Session, patient_id: int, patient: schemas.PatientUpdate):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not db_patient:
        return None
    
    update_data = patient.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patient, field, value)
    
    db.commit()
    db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not db_patient:
        return False
    
    db.delete(db_patient)
    db.commit()
    return True

# Drug CRUD

def create_drug(db: Session, drug: schemas.DrugCreate):
    db_drug = models.Drug(**drug.dict())
    db.add(db_drug)
    db.commit()
    db.refresh(db_drug)
    return db_drug

def get_drugs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Drug).offset(skip).limit(limit).all()

def get_drug(db: Session, drug_id: int):
    return db.query(models.Drug).filter(models.Drug.id == drug_id).first()

def update_drug(db: Session, drug_id: int, drug: schemas.DrugUpdate):
    db_drug = db.query(models.Drug).filter(models.Drug.id == drug_id).first()
    if not db_drug:
        return None
    
    update_data = drug.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_drug, field, value)
    
    db.commit()
    db.refresh(db_drug)
    return db_drug

def delete_drug(db: Session, drug_id: int):
    db_drug = db.query(models.Drug).filter(models.Drug.id == drug_id).first()
    if not db_drug:
        return False
    
    db.delete(db_drug)
    db.commit()
    return True

# Prescription CRUD

def create_prescription(db: Session, prescription: schemas.PrescriptionCreate):
    db_presc = models.Prescription(**prescription.dict())
    db.add(db_presc)
    db.commit()
    db.refresh(db_presc)
    return db_presc

def get_prescriptions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Prescription).offset(skip).limit(limit).all()

def get_prescription(db: Session, prescription_id: int):
    return db.query(models.Prescription).filter(models.Prescription.id == prescription_id).first()

def update_prescription(db: Session, prescription_id: int, prescription: schemas.PrescriptionUpdate):
    db_presc = db.query(models.Prescription).filter(models.Prescription.id == prescription_id).first()
    if not db_presc:
        return None
    
    update_data = prescription.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_presc, field, value)
    
    db.commit()
    db.refresh(db_presc)
    return db_presc

def delete_prescription(db: Session, prescription_id: int):
    db_presc = db.query(models.Prescription).filter(models.Prescription.id == prescription_id).first()
    if not db_presc:
        return False
    
    db.delete(db_presc)
    db.commit()
    return True

# Analysis CRUD

def create_analysis(db: Session, analysis: schemas.AnalysisCreate):
    db_analysis = models.Analysis(**analysis.dict())
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis

def get_analyses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Analysis).offset(skip).limit(limit).all()

def get_analysis(db: Session, analysis_id: int):
    return db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()

def update_analysis(db: Session, analysis_id: int, analysis: schemas.AnalysisUpdate):
    db_analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
    if not db_analysis:
        return None
    
    update_data = analysis.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_analysis, field, value)
    
    db.commit()
    db.refresh(db_analysis)
    return db_analysis

def delete_analysis(db: Session, analysis_id: int):
    db_analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
    if not db_analysis:
        return False
    
    db.delete(db_analysis)
    db.commit()
    return True

# Report CRUD

def create_report(db: Session, report: schemas.ReportCreate) -> models.Report:
    db_report = models.Report(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_reports(db: Session, skip: int = 0, limit: int = 100) -> List[models.Report]:
    return db.query(models.Report).offset(skip).limit(limit).all()

def get_report(db: Session, report_id: int) -> Optional[models.Report]:
    return db.query(models.Report).filter(models.Report.id == report_id).first()

def delete_report(db: Session, report_id: int) -> bool:
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if report:
        db.delete(report)
        db.commit()
        return True
    return False

# AuditLog CRUD

def create_audit_log(db: Session, audit_log: schemas.AuditLogCreate) -> models.AuditLog:
    db_audit_log = models.AuditLog(**audit_log.dict())
    db.add(db_audit_log)
    db.commit()
    db.refresh(db_audit_log)
    return db_audit_log

def get_audit_logs(db: Session, skip: int = 0, limit: int = 100) -> List[models.AuditLog]:
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

def get_audit_logs_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.AuditLog]:
    return db.query(models.AuditLog).filter(models.AuditLog.user_id == user_id).order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

def get_audit_logs_by_action(db: Session, action: str, skip: int = 0, limit: int = 100) -> List[models.AuditLog]:
    return db.query(models.AuditLog).filter(models.AuditLog.action == action).order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

# Enhanced CRUD operations with audit logging
def create_patient_with_audit(db: Session, patient: schemas.PatientCreate, user_id: int) -> models.Patient:
    db_patient = create_patient(db, patient)
    
    # Create audit log
    create_audit_log(db, schemas.AuditLogCreate(
        action="create_patient",
        user_id=user_id,
        details=f"Created patient: {db_patient.name} (ID: {db_patient.id})"
    ))
    
    return db_patient

def update_patient_with_audit(db: Session, patient_id: int, patient: schemas.PatientUpdate, user_id: int) -> Optional[models.Patient]:
    db_patient = update_patient(db, patient_id, patient)
    
    if db_patient:
        # Create audit log
        create_audit_log(db, schemas.AuditLogCreate(
            action="update_patient",
            user_id=user_id,
            details=f"Updated patient: {db_patient.name} (ID: {db_patient.id})"
        ))
    
    return db_patient

def delete_patient_with_audit(db: Session, patient_id: int, user_id: int) -> bool:
    patient = get_patient(db, patient_id)
    success = delete_patient(db, patient_id)
    
    if success and patient:
        # Create audit log
        create_audit_log(db, schemas.AuditLogCreate(
            action="delete_patient",
            user_id=user_id,
            details=f"Deleted patient: {patient.name} (ID: {patient_id})"
        ))
    
    return success

def create_drug_with_audit(db: Session, drug: schemas.DrugCreate, user_id: int) -> models.Drug:
    db_drug = create_drug(db, drug)
    
    # Create audit log
    create_audit_log(db, schemas.AuditLogCreate(
        action="create_drug",
        user_id=user_id,
        details=f"Created drug: {db_drug.name} (ID: {db_drug.id})"
    ))
    
    return db_drug

def update_drug_with_audit(db: Session, drug_id: int, drug: schemas.DrugUpdate, user_id: int) -> Optional[models.Drug]:
    db_drug = update_drug(db, drug_id, drug)
    
    if db_drug:
        # Create audit log
        create_audit_log(db, schemas.AuditLogCreate(
            action="update_drug",
            user_id=user_id,
            details=f"Updated drug: {db_drug.name} (ID: {db_drug.id})"
        ))
    
    return db_drug

def delete_drug_with_audit(db: Session, drug_id: int, user_id: int) -> bool:
    drug = get_drug(db, drug_id)
    success = delete_drug(db, drug_id)
    
    if success and drug:
        # Create audit log
        create_audit_log(db, schemas.AuditLogCreate(
            action="delete_drug",
            user_id=user_id,
            details=f"Deleted drug: {drug.name} (ID: {drug_id})"
        ))
    
    return success

def create_prescription_with_audit(db: Session, prescription: schemas.PrescriptionCreate, user_id: int) -> models.Prescription:
    db_prescription = create_prescription(db, prescription)
    
    # Create audit log
    create_audit_log(db, schemas.AuditLogCreate(
        action="create_prescription",
        user_id=user_id,
        details=f"Created prescription: Patient {db_prescription.patient_id}, Drug {db_prescription.drug_id} (ID: {db_prescription.id})"
    ))
    
    return db_prescription

def update_prescription_with_audit(db: Session, prescription_id: int, prescription: schemas.PrescriptionUpdate, user_id: int) -> Optional[models.Prescription]:
    db_prescription = update_prescription(db, prescription_id, prescription)
    
    if db_prescription:
        # Create audit log
        create_audit_log(db, schemas.AuditLogCreate(
            action="update_prescription",
            user_id=user_id,
            details=f"Updated prescription: Patient {db_prescription.patient_id}, Drug {db_prescription.drug_id} (ID: {db_prescription.id})"
        ))
    
    return db_prescription

def delete_prescription_with_audit(db: Session, prescription_id: int, user_id: int) -> bool:
    prescription = get_prescription(db, prescription_id)
    success = delete_prescription(db, prescription_id)
    
    if success and prescription:
        # Create audit log
        create_audit_log(db, schemas.AuditLogCreate(
            action="delete_prescription",
            user_id=user_id,
            details=f"Deleted prescription: Patient {prescription.patient_id}, Drug {prescription.drug_id} (ID: {prescription_id})"
        ))
    
    return success

def create_analysis_with_audit(db: Session, analysis: schemas.AnalysisCreate, user_id: int) -> models.Analysis:
    db_analysis = create_analysis(db, analysis)
    
    # Create audit log
    create_audit_log(db, schemas.AuditLogCreate(
        action="create_analysis",
        user_id=user_id,
        details=f"Created analysis: {db_analysis.type} (ID: {db_analysis.id})"
    ))
    
    return db_analysis

def update_analysis_with_audit(db: Session, analysis_id: int, analysis: schemas.AnalysisUpdate, user_id: int) -> Optional[models.Analysis]:
    db_analysis = update_analysis(db, analysis_id, analysis)
    
    if db_analysis:
        # Create audit log
        create_audit_log(db, schemas.AuditLogCreate(
            action="update_analysis",
            user_id=user_id,
            details=f"Updated analysis: {db_analysis.type} (ID: {db_analysis.id})"
        ))
    
    return db_analysis

def delete_analysis_with_audit(db: Session, analysis_id: int, user_id: int) -> bool:
    analysis = get_analysis(db, analysis_id)
    success = delete_analysis(db, analysis_id)
    
    if success and analysis:
        # Create audit log
        create_audit_log(db, schemas.AuditLogCreate(
            action="delete_analysis",
            user_id=user_id,
            details=f"Deleted analysis: {analysis.type} (ID: {analysis_id})"
        ))
    
    return success 