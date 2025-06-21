from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import MedicationOrder, User, UserRole, MedicationAdministration, Drug
from schemas import MedicationAdministrationOut, MedicationAdministrationCreate
from dependencies import require_role, get_db, get_current_user
from crud import create_administration_and_decrement_stock

router = APIRouter(prefix="/administrations", tags=["administrations"])

@router.post("/", response_model=MedicationAdministrationOut, dependencies=[Depends(require_role("nurse"))])
def create_administration(
    admin: MedicationAdministrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate order exists
    order = db.query(MedicationOrder).filter(MedicationOrder.id == admin.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Set nurse_id from current user
    admin.nurse_id = current_user.id
    
    administration = create_administration_and_decrement_stock(db, admin, order.drug_id)
    return administration

@router.get("/", response_model=list[MedicationAdministrationOut], dependencies=[Depends(require_role("nurse"))])
def get_administrations(db: Session = Depends(get_db)):
    return db.query(MedicationAdministration).all() 