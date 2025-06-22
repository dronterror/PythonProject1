from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import MedicationOrder, User, UserRole, MedicationAdministration, Drug
from schemas import MedicationAdministrationOut, MedicationAdministrationCreate
from dependencies import require_role, get_db, get_current_user
from crud import create_administration_and_decrement_stock, bulk_create_administrations
from models import OrderStatus
import uuid

router = APIRouter(prefix="/administrations", tags=["administrations"])

@router.post("/", response_model=MedicationAdministrationOut, dependencies=[Depends(require_role("nurse"))])
def create_administration(
    admin: MedicationAdministrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Critical endpoint: Record medication administration and decrement stock atomically
    This is the "final boss" endpoint that implements the core business logic
    """
    try:
        # Step A: Fetch the Order from the database using the order_id from the request body
        order = db.query(MedicationOrder).filter(MedicationOrder.id == admin.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status != OrderStatus.active:
            raise HTTPException(status_code=400, detail="Order is not active")
        
        # Step B: Call the atomic CRUD function with proper parameters
        # Pass order.id, the trusted order.drug_id, and current_user.id as nurse_id
        administration = create_administration_and_decrement_stock(
            db, 
            order_id=order.id, 
            drug_id=order.drug_id,  # Use the trusted drug_id from the order
            nurse_id=current_user.id
        )
        
        return administration
        
    except ValueError as e:
        # Step C: Convert ValueError to appropriate HTTPException
        if "Insufficient stock" in str(e):
            raise HTTPException(status_code=400, detail="Insufficient stock")
        elif "Order not found or not active" in str(e):
            raise HTTPException(status_code=404, detail="Order not found or not active")
        elif "Order not found" in str(e):
            raise HTTPException(status_code=404, detail="Order not found")
        elif "Drug not found" in str(e):
            raise HTTPException(status_code=404, detail="Drug not found")
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Debug: print exception type and message
        import sys
        print(f"DEBUG: Exception type: {type(e)}, message: {e}", file=sys.stderr)
        if isinstance(e, HTTPException):
            raise e
        # Handle any other unexpected errors
        raise HTTPException(status_code=500, detail="Internal server error during administration")

@router.post("/bulk", response_model=List[MedicationAdministrationOut], dependencies=[Depends(require_role("nurse"))])
def create_bulk_administrations(
    order_ids: List[uuid.UUID],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk administration endpoint for efficient nurse workflow.
    Processes multiple administrations in a single transaction.
    """
    try:
        administrations = bulk_create_administrations(db, order_ids, current_user.id)
        return administrations
    except ValueError as e:
        if "Insufficient stock" in str(e):
            raise HTTPException(status_code=400, detail="Insufficient stock for one or more orders")
        elif "Order not found" in str(e):
            raise HTTPException(status_code=404, detail="One or more orders not found")
        elif "Order not active" in str(e):
            raise HTTPException(status_code=400, detail="One or more orders are not active")
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error during bulk administration")

@router.get("/", response_model=list[MedicationAdministrationOut], dependencies=[Depends(require_role("nurse"))])
def get_administrations(db: Session = Depends(get_db)):
    return db.query(MedicationAdministration).all() 