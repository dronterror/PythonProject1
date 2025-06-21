"""
ValMed Healthcare Analytics Platform - Pydantic Schemas

This module defines all Pydantic models for request/response validation:
- User management schemas
- Patient management schemas  
- Drug management schemas
- Prescription management schemas
- Analysis management schemas
- Report and audit log schemas

These schemas ensure data validation, serialization, and API documentation.

Author: ValMed Development Team
Version: 1.0.0
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
import enum
from models import UserRole

# ============================================================================
# USER MANAGEMENT SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr        # User's email address (validated format)
    role: UserRole         # User's role in the system

class UserCreate(UserBase):
    """Schema for creating new users"""
    password: str          # Plain text password (will be hashed)

class UserUpdate(BaseModel):
    """Schema for updating users (all fields optional)"""
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None

class UserOut(UserBase):
    """Schema for user responses"""
    id: int                # User ID
    
    class Config:
        from_attributes = True  # Allow ORM model conversion

# ============================================================================
# PATIENT MANAGEMENT SCHEMAS
# ============================================================================

class PatientBase(BaseModel):
    """Base patient model with common fields"""
    name: str              # Patient's full name
    date_of_birth: date    # Patient's date of birth
    gender: str            # Patient's gender
    contact_info: Optional[str] = None    # Contact information
    diagnosis: Optional[str] = None       # Medical diagnosis

class PatientCreate(PatientBase):
    """Schema for creating new patients"""
    pass

class PatientUpdate(BaseModel):
    """Schema for updating patients (all fields optional)"""
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    contact_info: Optional[str] = None
    diagnosis: Optional[str] = None

class PatientOut(PatientBase):
    """Schema for patient responses"""
    id: int                # Patient ID
    blockchain_record_id: Optional[str] = None  # Blockchain record reference
    
    class Config:
        from_attributes = True

# ============================================================================
# DRUG MANAGEMENT SCHEMAS
# ============================================================================

class DrugBase(BaseModel):
    """Base drug model with common fields"""
    name: str              # Drug name
    manufacturer: Optional[str] = None    # Drug manufacturer
    price_per_unit: float  # Price per unit (required for cost analysis)
    effectiveness_score: Optional[float] = None  # Effectiveness rating (0-1)

class DrugCreate(DrugBase):
    """Schema for creating new drugs"""
    pass

class DrugUpdate(BaseModel):
    """Schema for updating drugs (all fields optional)"""
    name: Optional[str] = None
    manufacturer: Optional[str] = None
    price_per_unit: Optional[float] = None
    effectiveness_score: Optional[float] = None

class DrugOut(DrugBase):
    """Schema for drug responses"""
    id: int                # Drug ID
    
    class Config:
        from_attributes = True

# ============================================================================
# PRESCRIPTION MANAGEMENT SCHEMAS
# ============================================================================

class PrescriptionBase(BaseModel):
    """Base prescription model with common fields"""
    patient_id: int        # Reference to patient
    drug_id: int           # Reference to drug
    dosage: str            # Dosage instructions
    duration: str          # Treatment duration

class PrescriptionCreate(PrescriptionBase):
    """Schema for creating new prescriptions"""
    pass

class PrescriptionUpdate(BaseModel):
    """Schema for updating prescriptions (all fields optional)"""
    patient_id: Optional[int] = None
    drug_id: Optional[int] = None
    dosage: Optional[str] = None
    duration: Optional[str] = None

class PrescriptionOut(PrescriptionBase):
    """Schema for prescription responses"""
    id: int                # Prescription ID
    prescription_date: Optional[datetime] = None
    cost_at_time_of_prescription: Optional[float] = None
    effectiveness_at_time_of_prescription: Optional[float] = None
    calculated_icer: Optional[float] = None
    qaly_score: Optional[float] = None
    patient: PatientOut
    drug: DrugOut
    
    class Config:
        from_attributes = True

# ============================================================================
# ANALYSIS MANAGEMENT SCHEMAS
# ============================================================================

class AnalysisType(str, enum.Enum):
    """Analysis type enumeration"""
    ICER = "ICER"
    QALY = "QALY"
    BIA = "BIA"

class AnalysisBase(BaseModel):
    """Base analysis model with common fields"""
    type: AnalysisType
    input_data: str        # Input data for analysis
    result: Optional[str] = None    # Analysis results
    user_id: Optional[int] = None   # User who performed analysis

class AnalysisCreate(AnalysisBase):
    """Schema for creating new analyses"""
    pass

class AnalysisUpdate(BaseModel):
    """Schema for updating analyses (all fields optional)"""
    type: Optional[AnalysisType] = None
    input_data: Optional[str] = None
    result: Optional[str] = None
    user_id: Optional[int] = None

class AnalysisOut(AnalysisBase):
    """Schema for analysis responses"""
    id: int                # Analysis ID
    timestamp: datetime    # When analysis was performed
    
    class Config:
        from_attributes = True

# ============================================================================
# REPORT MANAGEMENT SCHEMAS
# ============================================================================

class ReportBase(BaseModel):
    """Base report model with common fields"""
    title: str             # Report title
    content: str           # Report content

class ReportCreate(ReportBase):
    """Schema for creating new reports"""
    pass

class ReportUpdate(BaseModel):
    """Schema for updating reports (all fields optional)"""
    title: Optional[str] = None
    content: Optional[str] = None

class ReportOut(ReportBase):
    """Schema for report responses"""
    id: int                # Report ID
    created_by: int        # User who created the report
    created_at: datetime   # When report was created
    creator: UserOut
    
    class Config:
        from_attributes = True

# ============================================================================
# AUDIT LOG SCHEMAS
# ============================================================================

class AuditLogBase(BaseModel):
    """Base audit log model with common fields"""
    action: str            # Action performed (create, update, delete, etc.)
    details: Optional[str] = None    # Additional details about the action
    ip_address: Optional[str] = None # IP address of the user
    user_agent: Optional[str] = None # User agent string

class AuditLogCreate(AuditLogBase):
    """Schema for creating new audit logs"""
    pass

class AuditLogOut(AuditLogBase):
    """Schema for audit log responses"""
    id: int                # Audit log ID
    user_id: Optional[int] = None
    timestamp: datetime    # When action was performed
    user: Optional[UserOut] = None
    
    class Config:
        from_attributes = True

# ============================================================================
# MEDICATION LOGISTICS SCHEMAS
# ============================================================================

class MedicationDrugBase(BaseModel):
    """Base medication drug model for inventory management"""
    name: str
    form: str
    strength: str
    current_stock: int
    low_stock_threshold: int

class MedicationDrugCreate(MedicationDrugBase):
    """Schema for creating new medication drugs"""
    pass

class MedicationDrugUpdate(BaseModel):
    """Schema for updating medication drugs (all fields optional)"""
    name: Optional[str] = None
    form: Optional[str] = None
    strength: Optional[str] = None
    current_stock: Optional[int] = None
    low_stock_threshold: Optional[int] = None

class MedicationDrugOut(MedicationDrugBase):
    """Schema for medication drug responses"""
    id: int
    
    class Config:
        from_attributes = True

class MedicationOrderBase(BaseModel):
    """Base medication order model"""
    patient_name: str
    patient_bed_number: str
    drug_id: int
    dosage: str
    schedule: str

class MedicationOrderCreate(MedicationOrderBase):
    """Schema for creating new medication orders"""
    pass

class MedicationOrderUpdate(BaseModel):
    """Schema for updating medication orders (all fields optional)"""
    patient_name: Optional[str] = None
    patient_bed_number: Optional[str] = None
    drug_id: Optional[int] = None
    dosage: Optional[str] = None
    schedule: Optional[str] = None
    status: Optional[str] = None

class MedicationOrderOut(MedicationOrderBase):
    """Schema for medication order responses"""
    id: int
    status: str
    doctor_id: int
    created_at: datetime
    drug: MedicationDrugOut
    
    class Config:
        from_attributes = True

class MedicationAdministrationBase(BaseModel):
    """Base medication administration model"""
    order_id: int

class MedicationAdministrationCreate(MedicationAdministrationBase):
    """Schema for creating new medication administrations"""
    pass

class MedicationAdministrationOut(MedicationAdministrationBase):
    """Schema for medication administration responses"""
    id: int
    nurse_id: int
    administration_time: datetime
    status: str
    
    class Config:
        from_attributes = True

# ============================================================================
# MEDICATION LOGISTICS DASHBOARD SCHEMAS
# ============================================================================

class WardPatientOut(BaseModel):
    """Schema for ward patient view"""
    name: str
    bed_number: str
    active_orders: List[MedicationOrderOut]
    
    class Config:
        from_attributes = True

class LowStockAlert(BaseModel):
    """Schema for low stock alert"""
    drug: MedicationDrugOut
    current_stock: int
    threshold: int
    
    class Config:
        from_attributes = True

class PatientMedicationTask(BaseModel):
    """Schema for patient medication task"""
    patient_name: str
    bed_number: str
    order: MedicationOrderOut
    due_time: Optional[datetime] = None
    status: str  # 'due', 'completed', 'missed'
    
    class Config:
        from_attributes = True

# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None 