from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
import enum

class UserRole(str, enum.Enum):
    doctor = "doctor"
    nurse = "nurse"
    analyst = "analyst"

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    class Config:
        from_attributes = True

class PatientBase(BaseModel):
    name: str
    date_of_birth: date
    gender: str
    contact_info: Optional[str] = None
    diagnosis: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientOut(PatientBase):
    id: int
    blockchain_record_id: Optional[str] = None
    class Config:
        from_attributes = True

class DrugBase(BaseModel):
    name: str
    manufacturer: Optional[str] = None
    price_per_unit: float
    effectiveness_score: Optional[float] = None

class DrugCreate(DrugBase):
    pass

class DrugOut(DrugBase):
    id: int
    class Config:
        from_attributes = True

class PrescriptionBase(BaseModel):
    patient_id: int
    drug_id: int
    prescription_date: Optional[datetime] = None
    dosage: Optional[str] = None
    duration: Optional[str] = None
    cost_at_time_of_prescription: Optional[float] = None
    effectiveness_at_time_of_prescription: Optional[float] = None
    calculated_icer: Optional[float] = None
    qaly_score: Optional[float] = None

class PrescriptionCreate(PrescriptionBase):
    pass

class PrescriptionOut(PrescriptionBase):
    id: int
    class Config:
        from_attributes = True

class AnalysisBase(BaseModel):
    type: str
    input_data: str
    result: Optional[str] = None
    user_id: Optional[int] = None

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisOut(AnalysisBase):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

class ReportBase(BaseModel):
    title: str
    content: str
    created_by: Optional[int] = None

class ReportCreate(ReportBase):
    pass

class ReportOut(ReportBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class AuditLogBase(BaseModel):
    action: str
    user_id: Optional[int] = None
    details: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogOut(AuditLogBase):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True 