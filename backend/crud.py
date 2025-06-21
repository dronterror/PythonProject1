from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, func, select
from datetime import datetime, timedelta
import models, schemas
from passlib.context import CryptContext
from typing import List, Optional
from fastapi import HTTPException
import logging

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# User CRUD

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.hashed_password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        api_key=user.api_key,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Drug CRUD

def get_drug(db: Session, drug_id: int):
    return db.query(models.Drug).filter(models.Drug.id == drug_id).first()

def get_drugs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Drug).offset(skip).limit(limit).all()

def create_drug(db: Session, drug: schemas.DrugCreate):
    db_drug = models.Drug(**drug.dict())
    db.add(db_drug)
    db.commit()
    db.refresh(db_drug)
    return db_drug

def update_drug(db: Session, drug_id: int, drug: schemas.DrugUpdate):
    db_drug = get_drug(db, drug_id)
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

def get_low_stock_drugs(db: Session):
    """Get all drugs that have fallen below their low stock threshold"""
    return db.query(models.Drug).filter(
        models.Drug.current_stock <= models.Drug.low_stock_threshold
    ).all()

# Medication Order CRUD

def create_medication_order(db: Session, order: schemas.MedicationOrderCreate, doctor_id: int):
    db_order = models.MedicationOrder(**order.dict(), doctor_id=doctor_id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def create_with_doctor(db: Session, order_in: schemas.MedicationOrderCreate, doctor_id: int) -> models.MedicationOrder:
    """Create a medication order with the doctor_id from the authenticated user"""
    db_order = models.MedicationOrder(**order_in.dict(), doctor_id=doctor_id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_medication_orders(db: Session, skip: int = 0, limit: int = 100):
    """
    Get medication orders with administrations eagerly loaded.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of MedicationOrder objects with administrations eagerly loaded
    """
    return db.query(models.MedicationOrder).options(
        selectinload(models.MedicationOrder.administrations)
    ).offset(skip).limit(limit).all()

def get_medication_order(db: Session, order_id: int):
    """
    Get a single medication order with administrations eagerly loaded.
    
    Args:
        db: Database session
        order_id: ID of the order to retrieve
        
    Returns:
        MedicationOrder object with administrations eagerly loaded, or None if not found
    """
    return db.query(models.MedicationOrder).filter(
        models.MedicationOrder.id == order_id
    ).options(
        selectinload(models.MedicationOrder.administrations)
    ).first()

def update_medication_order(db: Session, order_id: int, order: schemas.MedicationOrderUpdate):
    db_order = get_medication_order(db, order_id)
    if not db_order:
        return None
    
    update_data = order.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order, field, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def delete_medication_order(db: Session, order_id: int):
    db_order = get_medication_order(db, order_id)
    if db_order:
        db.delete(db_order)
        db.commit()
    return db_order

def get_active_medication_orders(db: Session):
    """
    Get all active medication orders with administrations eagerly loaded.
    
    Args:
        db: Database session
        
    Returns:
        List of MedicationOrder objects with administrations eagerly loaded
    """
    return db.query(models.MedicationOrder).filter(
        models.MedicationOrder.status == "active"
    ).options(
        selectinload(models.MedicationOrder.administrations)
    ).all()

def get_multi_active(db: Session) -> list[models.MedicationOrder]:
    """
    Get all active medication orders for the nurse's dashboard with administrations eagerly loaded.
    
    Args:
        db: Database session
        
    Returns:
        List of MedicationOrder objects with administrations eagerly loaded
    """
    return db.query(models.MedicationOrder).filter(
        models.MedicationOrder.status == models.OrderStatus.active
    ).options(
        selectinload(models.MedicationOrder.administrations)
    ).all()

def get_multi_by_doctor(db: Session, doctor_id: int) -> list[models.MedicationOrder]:
    """
    Get all orders created by a specific doctor with their administrations efficiently loaded.
    
    Args:
        db: Database session
        doctor_id: ID of the doctor whose orders to retrieve
        
    Returns:
        List of MedicationOrder objects with administrations eagerly loaded
    """
    return db.query(models.MedicationOrder).filter(
        models.MedicationOrder.doctor_id == doctor_id
    ).options(
        selectinload(models.MedicationOrder.administrations)
    ).all()

# Medication Administration CRUD

def create_medication_administration(db: Session, administration: schemas.MedicationAdministrationCreate, nurse_id: int):
    """Create a medication administration record and update drug stock atomically"""
    try:
        # Get the order to find the drug
        order = get_medication_order(db, administration.order_id)
        if not order:
            raise ValueError("Medication order not found")
        
        # Create administration record
        db_administration = models.MedicationAdministration(
            **administration.dict(),
            nurse_id=nurse_id
        )
        db.add(db_administration)
        
        # Update drug stock (decrement by 1 for each administration)
        drug = get_drug(db, order.drug_id)
        if not drug:
            raise ValueError("Drug not found")
        
        if drug.current_stock <= 0:
            raise ValueError("Insufficient drug stock")
        
        drug.current_stock -= 1
        
        db.commit()
        db.refresh(db_administration)
        return db_administration
        
    except Exception as e:
        db.rollback()
        raise e

def get_medication_administrations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MedicationAdministration).offset(skip).limit(limit).all()

def get_medication_administration(db: Session, administration_id: int):
    return db.query(models.MedicationAdministration).filter(
        models.MedicationAdministration.id == administration_id
    ).first()

def get_medication_administrations_by_order(db: Session, order_id: int):
    """Get all administrations for a specific order"""
    return db.query(models.MedicationAdministration).filter(
        models.MedicationAdministration.order_id == order_id
    ).all()

def get_medication_administrations_by_nurse(db: Session, nurse_id: int):
    """Get all administrations performed by a specific nurse"""
    return db.query(models.MedicationAdministration).filter(
        models.MedicationAdministration.nurse_id == nurse_id
    ).all()

def create_administration_and_decrement_stock(db: Session, order_id: int, drug_id: int, nurse_id: int):
    """
    Critical function: Atomic transaction to create administration and decrement stock
    This is the "final boss" function that implements the core business logic
    """
    try:
        # Step 1: Fetch the order and validate it exists and is active
        order = db.query(models.MedicationOrder).filter(
            models.MedicationOrder.id == order_id,
            models.MedicationOrder.status == models.OrderStatus.active
        ).first()
        if order is None:
            raise ValueError("Order not found or not active")
        
        # Step 2: Get the drug (removed with_for_update for SQLAlchemy 1.x compatibility)
        drug = db.query(models.Drug).filter(models.Drug.id == drug_id).first()
        
        if not drug:
            raise ValueError("Drug not found")
        
        # Step 3: Check if there's sufficient stock
        if drug.current_stock <= 0:
            raise ValueError("Insufficient stock")
        
        # Step 4: Create administration record
        administration = models.MedicationAdministration(
            order_id=order_id,
            nurse_id=nurse_id
        )
        db.add(administration)
        
        # Step 5: Decrement stock by 1 (atomic operation)
        drug.current_stock -= 1
        
        # Step 6: Mark order as completed (MVP: assume one administration per order)
        order.status = models.OrderStatus.completed
        db.add(order)
        
        # Step 7: Commit the entire transaction
        db.commit()
        db.refresh(administration)
        
        logger.info(f"Successfully administered medication: Order {order_id}, Drug {drug_id}, Nurse {nurse_id}")
        return administration
        
    except ValueError as e:
        # Rollback on business logic errors
        db.rollback()
        logger.error(f"Business logic error in administration: {e}")
        raise e
    except Exception as e:
        # Rollback on any other errors
        db.rollback()
        logger.error(f"Unexpected error in administration transaction: {e}")
        raise e

def create_administration_and_decrement_stock_legacy(db: Session, admin: schemas.MedicationAdministrationCreate, drug_id: int):
    """Legacy function - kept for backward compatibility"""
    try:
        # Fetch order and check existence
        order = db.query(models.MedicationOrder).filter(models.MedicationOrder.id == admin.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check if nurse_id is provided
        if not admin.nurse_id:
            raise HTTPException(status_code=400, detail="Nurse ID is required")
        
        # Fetch nurse and check existence
        nurse = db.query(models.User).filter(models.User.id == admin.nurse_id, models.User.role == models.UserRole.nurse).first()
        if not nurse:
            raise HTTPException(status_code=404, detail="Nurse not found or not a nurse")
        
        # Lock the drug row for update (WARNING: SQLite does not enforce row-level locks)
        drug = db.query(models.Drug).filter(models.Drug.id == drug_id).first()
        
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        
        # Use dosage from order
        dosage = order.dosage
        if drug.current_stock < dosage:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        
        # Create administration record
        administration = models.MedicationAdministration(
            order_id=admin.order_id,
            nurse_id=admin.nurse_id
        )
        db.add(administration)
        
        # Decrement stock
        drug.current_stock -= dosage
        if drug.current_stock < 0:
            logger.error(f"Negative stock for drug {drug.id} after administration!")
            raise HTTPException(status_code=500, detail="Negative stock error")
        db.add(drug)
        
        # Mark order as completed if this was the last administration (MVP: assume one admin per order)
        order.status = models.OrderStatus.completed
        db.add(order)
        
        db.commit()
        db.refresh(administration)
        return administration
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction failed: {e}")
        raise 