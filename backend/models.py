from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
import enum
from datetime import datetime

class UserRole(enum.Enum):
    doctor = "doctor"
    nurse = "nurse"
    analyst = "analyst"
    admin = "admin"
    pharmacist = "pharmacist"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    reports = relationship("Report", back_populates="creator")
    audit_logs = relationship("AuditLog", back_populates="user")

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    contact_info = Column(String)
    diagnosis = Column(String)
    blockchain_record_id = Column(String)  # For PoC
    prescriptions = relationship("Prescription", back_populates="patient")

class Drug(Base):
    __tablename__ = "drugs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    manufacturer = Column(String)
    price_per_unit = Column(Float, nullable=False)
    effectiveness_score = Column(Float)
    prescriptions = relationship("Prescription", back_populates="drug")

class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    drug_id = Column(Integer, ForeignKey("drugs.id"))
    prescription_date = Column(DateTime)
    dosage = Column(String)
    duration = Column(String)
    cost_at_time_of_prescription = Column(Float)
    effectiveness_at_time_of_prescription = Column(Float)
    calculated_icer = Column(Float)
    qaly_score = Column(Float)
    patient = relationship("Patient", back_populates="prescriptions")
    drug = relationship("Drug", back_populates="prescriptions")

class AnalysisType(enum.Enum):
    ICER = "ICER"
    QALY = "QALY"
    BIA = "BIA"  # Budget Impact Analysis

class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(AnalysisType), nullable=False)
    input_data = Column(String)  # JSON or stringified input
    result = Column(String)      # JSON or stringified result
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    creator = relationship("User", back_populates="reports")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text)
    ip_address = Column(String)
    user_agent = Column(String)
    user = relationship("User", back_populates="audit_logs")

# ============================================================================
# MEDICATION LOGISTICS MODELS (New MVP Feature)
# ============================================================================

class MedicationDrug(Base):
    """Drug inventory for medication logistics (separate from ICER drugs)"""
    __tablename__ = "medication_drugs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    form = Column(String, nullable=False)  # e.g., "Tablet", "Ampoule"
    strength = Column(String, nullable=False)  # e.g., "500mg"
    current_stock = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)

class MedicationOrder(Base):
    """Medication orders (prescriptions) for the logistics system"""
    __tablename__ = "medication_orders"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, nullable=False)
    patient_bed_number = Column(String, nullable=False)
    drug_id = Column(Integer, ForeignKey("medication_drugs.id"), nullable=False)
    dosage = Column(String, nullable=False)
    schedule = Column(String, nullable=False)  # e.g., "Twice a day"
    status = Column(String, default="active")  # 'active', 'discontinued'
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    drug = relationship("MedicationDrug")
    doctor = relationship("User")
    administrations = relationship("MedicationAdministration", back_populates="order")

class MedicationAdministration(Base):
    """Medication administration records"""
    __tablename__ = "medication_administrations"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("medication_orders.id"), nullable=False)
    nurse_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    administration_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")  # 'completed', 'missed_exception'
    
    # Relationships
    order = relationship("MedicationOrder", back_populates="administrations")
    nurse = relationship("User") 