from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from models import Drug, User, UserRole, MedicationOrder, OrderStatus
from schemas import MedicationOrderOut, MedicationOrderCreate
from dependencies import require_role, get_db, get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=MedicationOrderOut, dependencies=[Depends(require_role("doctor"))])
def create_order(order: MedicationOrderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Validate drug exists
    drug = db.query(Drug).filter(Drug.id == order.drug_id).first()
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    # Validate doctor exists
    doctor = db.query(User).filter(User.id == current_user.id, User.role == UserRole.doctor).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found or not a doctor")
    db_order = MedicationOrder(
        **order.dict(),
        status=OrderStatus.active,
        doctor_id=current_user.id
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/", response_model=List[MedicationOrderOut], dependencies=[Depends(get_current_user)])
def get_orders(db: Session = Depends(get_db), skip: int = 0, limit: int = Query(100, le=100)):
    return db.query(MedicationOrder).filter(MedicationOrder.status == OrderStatus.active).offset(skip).limit(limit).all() 