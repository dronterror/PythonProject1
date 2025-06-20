from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext

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

# Report CRUD

def create_report(db: Session, report: schemas.ReportCreate):
    db_report = models.Report(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_reports(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Report).offset(skip).limit(limit).all()

def get_report(db: Session, report_id: int):
    return db.query(models.Report).filter(models.Report.id == report_id).first()

# AuditLog CRUD

def create_audit_log(db: Session, audit_log: schemas.AuditLogCreate):
    db_log = models.AuditLog(**audit_log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_audit_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AuditLog).offset(skip).limit(limit).all()

def get_audit_log(db: Session, log_id: int):
    return db.query(models.AuditLog).filter(models.AuditLog.id == log_id).first() 