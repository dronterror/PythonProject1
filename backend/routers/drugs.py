from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
from models import Drug
from schemas import DrugOut, DrugCreate, DrugUpdate, DrugTransferCreate, DrugTransferOut
from dependencies import require_role, get_db, get_current_user
from crud import create_drug, update_drug, get_drugs, get_low_stock_drugs, get_formulary, get_inventory_status, transfer_drug_stock

router = APIRouter(prefix="/drugs", tags=["drugs"])

@router.post("/", response_model=DrugOut, dependencies=[Depends(require_role("pharmacist"))])
def create_drug_endpoint(drug: DrugCreate, db: Session = Depends(get_db)):
    # Check for duplicate
    exists = db.query(Drug).filter_by(name=drug.name, form=drug.form, strength=drug.strength).first()
    if exists:
        raise HTTPException(status_code=400, detail="Drug with same name, form, and strength already exists")
    
    return create_drug(db, drug)

@router.put("/{drug_id}", response_model=DrugOut, dependencies=[Depends(require_role("pharmacist"))])
def update_drug_endpoint(drug_id: uuid.UUID, drug: DrugUpdate, db: Session = Depends(get_db)):
    db_drug = update_drug(db, drug_id, drug)
    if not db_drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    return db_drug

@router.post("/transfer", response_model=DrugTransferOut, dependencies=[Depends(require_role("pharmacist"))])
def transfer_drug_stock_endpoint(
    transfer: DrugTransferCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Transfer drug stock between wards.
    Only pharmacists can perform drug stock transfers.
    """
    try:
        return transfer_drug_stock(db, transfer, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # Re-raise HTTPExceptions (like 404 for drug not found)
        raise

@router.get("/low-stock", response_model=List[DrugOut], dependencies=[Depends(require_role("pharmacist"))])
def get_low_stock_drugs_endpoint(db: Session = Depends(get_db), skip: int = 0, limit: int = Query(100, le=100)):
    drugs = get_low_stock_drugs(db)
    return drugs[skip:skip + limit]

@router.get("/", response_model=List[DrugOut], dependencies=[Depends(get_current_user)])
def get_drugs_endpoint(db: Session = Depends(get_db), skip: int = 0, limit: int = Query(100, le=100)):
    return get_drugs(db, skip, limit)

@router.get("/formulary", response_model=List[Dict[str, Any]], dependencies=[Depends(require_role("doctor"))])
def get_formulary_endpoint(db: Session = Depends(get_db)):
    """
    Get the static formulary list for doctors to use when prescribing.
    Returns lightweight drug information (id, name, form, strength).
    """
    # TODO: Add Redis caching here for improved performance
    return get_formulary(db)

@router.get("/inventory/status", response_model=Dict[str, Dict[str, Any]], dependencies=[Depends(require_role("doctor"))])
def get_inventory_status_endpoint(db: Session = Depends(get_db)):
    """
    Get real-time inventory status for all drugs.
    Returns a lightweight mapping of drug_id to stock count and status.
    """
    # TODO: Add Redis caching here for improved performance
    return get_inventory_status(db) 