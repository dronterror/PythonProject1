from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from models import Drug, User, UserRole, MedicationOrder, OrderStatus
from schemas import MedicationOrderOut, MedicationOrderCreate
from dependencies import require_role, require_roles, get_db, get_current_user
from crud import create_with_doctor, get_multi_active, get_multi_by_doctor

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=MedicationOrderOut, dependencies=[Depends(require_role("doctor"))])
def create_order(order: MedicationOrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Validate drug exists
    drug = db.query(Drug).filter(Drug.id == order.drug_id).first()
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    
    # Validate doctor exists (redundant check since require_role already validates this)
    if current_user.role != UserRole.doctor:
        raise HTTPException(status_code=403, detail="Only doctors can create orders")
    
    # Create the order using the new CRUD function
    db_order = create_with_doctor(db, order, current_user.id)
    return db_order

@router.get("/my-orders/", response_model=List[MedicationOrderOut], dependencies=[Depends(require_role("doctor"))])
def get_my_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get all orders created by the current doctor with administration status.
    This endpoint allows doctors to see the status of their prescriptions.
    """
    orders = get_multi_by_doctor(db, current_user.id)
    return orders

@router.get("/active-mar/", response_model=List[MedicationOrderOut], dependencies=[Depends(require_roles(["nurse", "pharmacist"]))])
def get_active_mar(db: Session = Depends(get_db)):
    """
    Get all active orders for the Medication Administration Record (MAR).
    This endpoint allows nurses and pharmacists to view active prescriptions.
    """
    active_orders = get_multi_active(db)
    return active_orders

@router.get("/", response_model=List[MedicationOrderOut], dependencies=[Depends(get_current_user)])
def get_orders(db: Session = Depends(get_db), skip: int = 0, limit: int = Query(100, le=100)):
    # Use the new CRUD function to get only active orders
    active_orders = get_multi_active(db)
    return active_orders[skip:skip + limit] 