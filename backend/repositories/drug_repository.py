from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
import uuid

from models import Drug, DrugTransfer


class DrugRepository:
    """
    Repository for drug data access.
    Handles all database operations related to drugs and drug transfers.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, drug_id: uuid.UUID) -> Optional[Drug]:
        """
        Get a single drug by ID.
        """
        return self.db.query(Drug).filter(Drug.id == drug_id).first()
    
    def get_by_name_form_strength(self, name: str, form: str, strength: str) -> Optional[Drug]:
        """
        Get a drug by its unique combination of name, form, and strength.
        """
        return self.db.query(Drug).filter(
            and_(
                Drug.name == name,
                Drug.form == form,
                Drug.strength == strength
            )
        ).first()
    
    def create(self, drug_data: Dict[str, Any]) -> Drug:
        """
        Create a new drug.
        """
        db_drug = Drug(**drug_data)
        self.db.add(db_drug)
        self.db.commit()
        self.db.refresh(db_drug)
        return db_drug
    
    def update(self, drug_id: uuid.UUID, update_data: Dict[str, Any]) -> Optional[Drug]:
        """
        Update a drug's information.
        """
        drug = self.db.query(Drug).filter(Drug.id == drug_id).first()
        if drug:
            for field, value in update_data.items():
                if hasattr(drug, field):
                    setattr(drug, field, value)
            self.db.commit()
            self.db.refresh(drug)
        return drug
    
    def list_all(self, skip: int = 0, limit: int = 100) -> List[Drug]:
        """
        Get all drugs with pagination.
        """
        return self.db.query(Drug).offset(skip).limit(limit).all()
    
    def list_all_for_cache(self) -> List[Drug]:
        """
        Get all drugs without pagination for caching purposes.
        Used for formulary and inventory status caching.
        """
        return self.db.query(Drug).all()
    
    def list_low_stock(self) -> List[Drug]:
        """
        Get all drugs that have fallen below their low stock threshold.
        """
        return self.db.query(Drug).filter(
            Drug.current_stock <= Drug.low_stock_threshold
        ).all()
    
    def get_formulary_data(self) -> List[Dict[str, Any]]:
        """
        Get lightweight formulary data for doctors.
        Returns only essential fields for prescribing.
        """
        drugs = self.db.query(Drug).all()
        return [
            {
                "id": str(drug.id),
                "name": drug.name,
                "form": drug.form,
                "strength": drug.strength
            }
            for drug in drugs
        ]
    
    def get_inventory_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get real-time inventory status for all drugs.
        Returns a mapping of drug_id to stock information.
        """
        drugs = self.db.query(Drug).all()
        inventory_status = {}
        
        for drug in drugs:
            is_low_stock = drug.current_stock <= drug.low_stock_threshold
            inventory_status[str(drug.id)] = {
                "current_stock": drug.current_stock,
                "low_stock_threshold": drug.low_stock_threshold,
                "is_low_stock": is_low_stock,
                "stock_status": "low" if is_low_stock else "adequate"
            }
        
        return inventory_status
    
    def update_stock(self, drug_id: uuid.UUID, new_stock: int) -> Optional[Drug]:
        """
        Update drug stock level.
        """
        drug = self.db.query(Drug).filter(Drug.id == drug_id).first()
        if drug:
            drug.current_stock = new_stock
            self.db.commit()
            self.db.refresh(drug)
        return drug
    
    def decrement_stock(self, drug_id: uuid.UUID, quantity: int) -> Optional[Drug]:
        """
        Decrement drug stock by specified quantity.
        Returns None if insufficient stock.
        """
        drug = self.db.query(Drug).filter(Drug.id == drug_id).first()
        if drug and drug.current_stock >= quantity:
            drug.current_stock -= quantity
            self.db.commit()
            self.db.refresh(drug)
            return drug
        return None
    
    def delete(self, drug_id: uuid.UUID) -> bool:
        """
        Delete a drug.
        """
        drug = self.db.query(Drug).filter(Drug.id == drug_id).first()
        if drug:
            self.db.delete(drug)
            self.db.commit()
            return True
        return False
    
    # Drug Transfer methods
    
    def create_transfer(self, transfer_data: Dict[str, Any], pharmacist_id: uuid.UUID) -> DrugTransfer:
        """
        Create a new drug transfer record.
        """
        db_transfer = DrugTransfer(
            **transfer_data,
            pharmacist_id=pharmacist_id
        )
        self.db.add(db_transfer)
        self.db.commit()
        self.db.refresh(db_transfer)
        return db_transfer
    
    def list_transfers(self, skip: int = 0, limit: int = 100) -> List[DrugTransfer]:
        """
        Get all drug transfers with pagination.
        """
        return self.db.query(DrugTransfer).offset(skip).limit(limit).all()
    
    def get_transfer_by_id(self, transfer_id: uuid.UUID) -> Optional[DrugTransfer]:
        """
        Get a single drug transfer by ID.
        """
        return self.db.query(DrugTransfer).filter(DrugTransfer.id == transfer_id).first() 