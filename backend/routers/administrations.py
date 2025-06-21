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
    """
    Critical endpoint: Record medication administration and decrement stock atomically
    This is the "final boss" endpoint that implements the core business logic
    """
    try:
        # Step A: Fetch the Order from the database using the order_id from the request body
        order = db.query(MedicationOrder).filter(MedicationOrder.id == admin.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status != "active":
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
        elif "Order not found" in str(e):
            raise HTTPException(status_code=404, detail="Order not found or not active")
        elif "Drug not found" in str(e):
            raise HTTPException(status_code=404, detail="Drug not found")
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(status_code=500, detail="Internal server error during administration")

@router.get("/", response_model=list[MedicationAdministrationOut], dependencies=[Depends(require_role("nurse"))])
def get_administrations(db: Session = Depends(get_db)):
    return db.query(MedicationAdministration).all() 