"""
ValMed Medication Logistics MVP - Pydantic Schemas

This module defines all Pydantic models for request/response validation:
- User management schemas
- Drug management schemas
- Medication order management schemas
- Medication administration schemas

These schemas ensure data validation, serialization, and API documentation.

Author: ValMed Development Team
Version: 1.0.0
"""

from pydantic import BaseModel, EmailStr, conint, Field
from typing import Optional, List
from datetime import date, datetime
import enum
from models import UserRole
import uuid

# ============================================================================
# USER MANAGEMENT SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr        # User's email address (validated format)
    role: UserRole         # User's role in the system

class UserCreate(UserBase):
    """Schema for creating new users"""
    hashed_password: str          # Plain text password (will be hashed)
    api_key: str           # API key for authentication

class UserUpdate(BaseModel):
    """Schema for updating users (all fields optional)"""
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    api_key: Optional[str] = None

class UserOut(UserBase):
    """Schema for user responses"""
    id: uuid.UUID          # User ID
    
    class Config:
        from_attributes = True  # Allow ORM model conversion

# ============================================================================
# DRUG MANAGEMENT SCHEMAS
# ============================================================================

class DrugBase(BaseModel):
    """Base drug model with common fields"""
    name: str              # Drug name
    form: str              # Drug form
    strength: str          # Drug strength
    current_stock: int = Field(..., ge=0)     # Current stock of the drug (non-negative)
    low_stock_threshold: int = Field(..., ge=0)  # Low stock threshold for the drug (non-negative)

class DrugCreate(DrugBase):
    """Schema for creating new drugs"""
    pass

class DrugUpdate(BaseModel):
    """Schema for updating drugs (all fields optional)"""
    name: Optional[str] = None
    form: Optional[str] = None
    strength: Optional[str] = None
    current_stock: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)

class DrugOut(DrugBase):
    """Schema for drug responses"""
    id: uuid.UUID          # Drug ID
    
    class Config:
        from_attributes = True

# ============================================================================
# MEDICATION ORDER SCHEMAS
# ============================================================================

class MedicationOrderBase(BaseModel):
    """Base medication order model"""
    patient_name: str
    drug_id: uuid.UUID
    dosage: conint(gt=0)
    schedule: str

class MedicationOrderCreate(MedicationOrderBase):
    """Schema for creating new medication orders"""
    pass

class MedicationOrderUpdate(BaseModel):
    """Schema for updating medication orders (all fields optional)"""
    patient_name: Optional[str] = None
    drug_id: Optional[uuid.UUID] = None
    dosage: Optional[conint(gt=0)] = None
    schedule: Optional[str] = None

class MedicationOrderOut(MedicationOrderBase):
    """Schema for medication order responses"""
    id: uuid.UUID
    status: str
    doctor_id: uuid.UUID
    created_at: datetime
    drug: DrugOut
    administrations: List["MedicationAdministrationOut"] = []
    
    class Config:
        from_attributes = True

# ============================================================================
# MEDICATION ADMINISTRATION SCHEMAS
# ============================================================================

class MedicationAdministrationBase(BaseModel):
    """Base medication administration model"""
    order_id: uuid.UUID

class MedicationAdministrationCreate(MedicationAdministrationBase):
    """Schema for creating new medication administrations"""
    nurse_id: Optional[uuid.UUID] = None

class MedicationAdministrationOut(MedicationAdministrationBase):
    """Schema for medication administration responses"""
    id: uuid.UUID
    nurse_id: uuid.UUID
    administration_time: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# ADDITIONAL MEDICATION LOGISTICS SCHEMAS
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
    drug: DrugOut
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