from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from models import Drug
from schemas import DrugOut, DrugCreate, DrugUpdate
from dependencies import require_role, get_db, get_current_user

router = APIRouter(prefix="/drugs", tags=["drugs"])

@router.post("/", response_model=DrugOut, dependencies=[Depends(require_role("pharmacist"))])
def create_drug(drug: DrugCreate, db: Session = Depends(get_db)):
    # Check for duplicate
    exists = db.query(Drug).filter_by(name=drug.name, form=drug.form, strength=drug.strength).first()
    if exists:
        raise HTTPException(status_code=400, detail="Drug with same name, form, and strength already exists")
    db_drug = Drug(**drug.dict())
    db.add(db_drug)
    db.commit()
    db.refresh(db_drug)
    return db_drug

@router.put("/{drug_id}", response_model=DrugOut, dependencies=[Depends(require_role("pharmacist"))])
def update_drug(drug_id: int, drug: DrugUpdate, db: Session = Depends(get_db)):
    db_drug = db.query(Drug).filter(Drug.id == drug_id).first()
    if not db_drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    for key, value in drug.dict(exclude_unset=True).items():
        setattr(db_drug, key, value)
    db.commit()
    db.refresh(db_drug)
    return db_drug

@router.get("/low-stock", response_model=List[DrugOut], dependencies=[Depends(require_role("pharmacist"))])
def get_low_stock_drugs(db: Session = Depends(get_db), skip: int = 0, limit: int = Query(100, le=100)):
    drugs = db.query(Drug).filter(Drug.current_stock <= Drug.low_stock_threshold).offset(skip).limit(limit).all()
    return drugs

@router.get("/", response_model=List[DrugOut], dependencies=[Depends(get_current_user)])
def get_drugs(db: Session = Depends(get_db), skip: int = 0, limit: int = Query(100, le=100)):
    return db.query(Drug).offset(skip).limit(limit).all() 