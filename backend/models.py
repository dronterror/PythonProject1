from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Enum, DateTime, Text, TIMESTAMP, func, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database import Base
import enum
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class UserRole(enum.Enum):
    doctor = "doctor"
    nurse = "nurse"
    pharmacist = "pharmacist"
    super_admin = "super_admin"

class OrderStatus(enum.Enum):
    active = "active"
    completed = "completed"
    discontinued = "discontinued"

class Hospital(Base):
    __tablename__ = "hospitals"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False, index=True)
    address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    wards = relationship("Ward", back_populates="hospital", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Hospital(id={self.id}, name={self.name})>"

class Ward(Base):
    __tablename__ = "wards"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('name', 'hospital_id'),)
    
    # Relationships
    hospital = relationship("Hospital", back_populates="wards")
    user_permissions = relationship("UserWardPermission", back_populates="ward", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ward(id={self.id}, name={self.name}, hospital_id={self.hospital_id})>"

class UserWardPermission(Base):
    __tablename__ = "user_ward_permissions"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    ward_id = Column(UUID(as_uuid=True), ForeignKey("wards.id"), nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('user_id', 'ward_id'),)
    
    # Relationships
    user = relationship("User", backref="ward_permissions")
    ward = relationship("Ward", back_populates="user_permissions")
    
    def __repr__(self):
        return f"<UserWardPermission(user_id={self.user_id}, ward_id={self.ward_id}, role={self.role})>"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=True)  # Made nullable since Keycloak handles auth
    auth_provider_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    role = Column(Enum(UserRole), nullable=False)
    __table_args__ = (UniqueConstraint('email'), UniqueConstraint('auth_provider_id'),)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

class Drug(Base):
    """Drug inventory for medication logistics"""
    __tablename__ = "drugs"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    form = Column(String, nullable=False)  # e.g., "Tablet", "Ampoule"
    strength = Column(String, nullable=False)  # e.g., "500mg"
    current_stock = Column(Integer, default=0, index=True)
    low_stock_threshold = Column(Integer, default=10)
    __table_args__ = (UniqueConstraint('name', 'form', 'strength'),)
    
    def __repr__(self):
        return f"<Drug(id={self.id}, name={self.name}, stock={self.current_stock})>"

class DrugTransfer(Base):
    """Drug stock transfers between wards"""
    __tablename__ = "drug_transfers"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    drug_id = Column(UUID(as_uuid=True), ForeignKey("drugs.id"), nullable=False, index=True)
    source_ward = Column(String, nullable=False, index=True)
    destination_ward = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    pharmacist_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    transfer_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    drug = relationship("Drug")
    pharmacist = relationship("User")
    
    def __repr__(self):
        return f"<DrugTransfer(id={self.id}, drug_id={self.drug_id}, from={self.source_ward}, to={self.destination_ward}, qty={self.quantity})>"

class MedicationOrder(Base):
    """Medication orders (prescriptions) for the logistics system"""
    __tablename__ = "medication_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    patient_name = Column(String, nullable=False, index=True)
    drug_id = Column(UUID(as_uuid=True), ForeignKey("drugs.id"), nullable=False, index=True)
    dosage = Column(Integer, nullable=False)  # Now integer for decrement logic
    schedule = Column(String, nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.active, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    drug = relationship("Drug")
    doctor = relationship("User")
    administrations = relationship("MedicationAdministration", back_populates="order")
    
    def __repr__(self):
        return f"<Order(id={self.id}, patient={self.patient_name}, drug_id={self.drug_id}, status={self.status})>"

class MedicationAdministration(Base):
    """Medication administration records"""
    __tablename__ = "medication_administrations"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("medication_orders.id"), nullable=False, index=True)
    nurse_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    administration_time = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    order = relationship("MedicationOrder", back_populates="administrations")
    nurse = relationship("User")
    
    def __repr__(self):
        return f"<Admin(id={self.id}, order_id={self.order_id}, nurse_id={self.nurse_id})>" 