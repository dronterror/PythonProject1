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

# ============================================================================
# USER MANAGEMENT SCHEMAS
# ============================================================================

class UserRole(str, enum.Enum):
    """User role enumeration for role-based access control"""
    doctor = "doctor"      # Can manage patients and prescriptions
    nurse = "nurse"        # Can view patient data
    analyst = "analyst"    # Can perform analytics and manage drugs
    admin = "admin"        # Full system access

class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr        # User's email address (validated format)
    role: UserRole         # User's role in the system

class UserCreate(UserBase):
    """Schema for creating new users"""
    password: str          # Plain text password (will be hashed)

class UserOut(UserBase):
    """Schema for user responses (excludes password)"""
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
    prescription_date: Optional[datetime] = None    # When prescribed
    dosage: Optional[str] = None                    # Dosage instructions
    duration: Optional[str] = None                  # Treatment duration
    cost_at_time_of_prescription: Optional[float] = None    # Cost when prescribed
    effectiveness_at_time_of_prescription: Optional[float] = None  # Effectiveness when prescribed
    calculated_icer: Optional[float] = None         # Incremental Cost-Effectiveness Ratio
    qaly_score: Optional[float] = None              # Quality-Adjusted Life Years score

class PrescriptionCreate(PrescriptionBase):
    """Schema for creating new prescriptions"""
    pass

class PrescriptionUpdate(BaseModel):
    """Schema for updating prescriptions (all fields optional)"""
    patient_id: Optional[int] = None
    drug_id: Optional[int] = None
    prescription_date: Optional[datetime] = None
    dosage: Optional[str] = None
    duration: Optional[str] = None
    cost_at_time_of_prescription: Optional[float] = None
    effectiveness_at_time_of_prescription: Optional[float] = None
    calculated_icer: Optional[float] = None
    qaly_score: Optional[float] = None

class PrescriptionOut(PrescriptionBase):
    """Schema for prescription responses"""
    id: int                # Prescription ID
    
    class Config:
        from_attributes = True

# ============================================================================
# ANALYSIS MANAGEMENT SCHEMAS
# ============================================================================

class AnalysisBase(BaseModel):
    """Base analysis model with common fields"""
    type: str              # Type of analysis performed
    input_data: str        # Input data for analysis
    result: Optional[str] = None    # Analysis results
    user_id: Optional[int] = None   # User who performed analysis

class AnalysisCreate(AnalysisBase):
    """Schema for creating new analyses"""
    pass

class AnalysisUpdate(BaseModel):
    """Schema for updating analyses (all fields optional)"""
    type: Optional[str] = None
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

class Report(ReportBase):
    """Schema for report responses"""
    id: int                # Report ID
    created_by: int        # User who created the report
    created_at: datetime   # When report was created
    
    class Config:
        from_attributes = True

class ReportOut(ReportBase):
    """Schema for report responses (alternative)"""
    id: int                # Report ID
    created_by: int        # User who created the report
    created_at: datetime   # When report was created
    
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
    user_id: int           # User who performed the action

class AuditLog(AuditLogBase):
    """Schema for audit log responses"""
    id: int                # Audit log ID
    user_id: int           # User who performed the action
    timestamp: datetime    # When action was performed
    
    class Config:
        from_attributes = True

class AuditLogOut(AuditLogBase):
    """Schema for audit log responses (alternative)"""
    id: int                # Audit log ID
    user_id: int           # User who performed the action
    timestamp: datetime    # When action was performed
    
    class Config:
        from_attributes = True 