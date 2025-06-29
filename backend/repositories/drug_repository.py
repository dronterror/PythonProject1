from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import and_, desc
from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime

from models import Drug, DrugTransfer, User


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
        CRITICAL: Uses explicit transaction boundary for data integrity.
        """
        with self.db.begin():
            db_drug = Drug(**drug_data)
            self.db.add(db_drug)
            self.db.flush()  # Flush to get the ID without committing
            self.db.refresh(db_drug)
            return db_drug
    
    def update(self, drug_id: uuid.UUID, update_data: Dict[str, Any]) -> Optional[Drug]:
        """
        Update a drug's information.
        CRITICAL: Uses explicit transaction boundary for data integrity.
        """
        with self.db.begin():
            drug = self.db.query(Drug).filter(Drug.id == drug_id).first()
            if drug:
                for field, value in update_data.items():
                    if hasattr(drug, field):
                        setattr(drug, field, value)
                self.db.flush()
                self.db.refresh(drug)
            return drug
    
    def list_all(self, skip: int = 0, limit: int = 100) -> List[Drug]:
        """
        Get all drugs with pagination.
        
        WARNING: This method uses OFFSET-based pagination which is inefficient for large datasets.
        Use list_all_with_cursor() for production workloads with large drug inventories.
        """
        return self.db.query(Drug).offset(skip).limit(limit).all()
    
    def list_all_with_cursor(
        self, 
        cursor: Optional[Union[str, uuid.UUID]] = None, 
        limit: int = 100,
        cursor_type: str = "name"
    ) -> Dict[str, Any]:
        """
        Get all drugs using KEYSET/CURSOR-based pagination for scalable performance.
        
        OFFSET-based pagination degrades performance with large datasets because PostgreSQL
        must scan and skip all preceding rows. Cursor-based pagination uses indexed columns
        to directly position the query, maintaining consistent O(log n) performance regardless
        of pagination depth.
        
        Args:
            cursor: The cursor value from the previous page (name or ID)
            limit: Maximum number of records to return
            cursor_type: Either "name" (lexicographic) or "id" for cursor positioning
            
        Returns:
            Dict containing 'drugs' list and 'next_cursor' for subsequent pagination
        """
        query = self.db.query(Drug)
        
        # Apply cursor-based filtering for scalable pagination
        if cursor:
            if cursor_type == "name":
                # Use name index for lexicographic pagination (useful for formulary browsing)
                query = query.filter(Drug.name > cursor)
                query = query.order_by(Drug.name)
            else:  # cursor_type == "id"
                # Use primary key index for stable pagination
                query = query.filter(Drug.id > cursor)
                query = query.order_by(Drug.id)
        else:
            # Default ordering for first page
            if cursor_type == "name":
                query = query.order_by(Drug.name)
            else:
                query = query.order_by(Drug.id)
        
        # Fetch one extra record to determine if there's a next page
        drugs = query.limit(limit + 1).all()
        
        has_next = len(drugs) > limit
        if has_next:
            drugs = drugs[:-1]  # Remove the extra record
        
        # Calculate next cursor
        next_cursor = None
        if has_next and drugs:
            last_drug = drugs[-1]
            next_cursor = last_drug.name if cursor_type == "name" else last_drug.id
        
        return {
            "drugs": drugs,
            "next_cursor": next_cursor,
            "has_next": has_next,
            "cursor_type": cursor_type
        }
    
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
        CRITICAL: Uses explicit transaction boundary for inventory integrity.
        """
        with self.db.begin():
            drug = self.db.query(Drug).filter(Drug.id == drug_id).first()
            if drug:
                drug.current_stock = new_stock
                self.db.flush()
                self.db.refresh(drug)
            return drug
    
    def decrement_stock(self, drug_id: uuid.UUID, quantity: int) -> Optional[Drug]:
        """
        Decrement drug stock by specified quantity.
        Returns None if insufficient stock.
        CRITICAL: Uses explicit transaction boundary to prevent stock inconsistencies.
        """
        with self.db.begin():
            drug = self.db.query(Drug).filter(Drug.id == drug_id).first()
            if drug and drug.current_stock >= quantity:
                drug.current_stock -= quantity
                self.db.flush()
                self.db.refresh(drug)
                return drug
            return None
    
    def delete(self, drug_id: uuid.UUID) -> bool:
        """
        Delete a drug.
        CRITICAL: Uses explicit transaction boundary for data integrity.
        """
        with self.db.begin():
            drug = self.db.query(Drug).filter(Drug.id == drug_id).first()
            if drug:
                self.db.delete(drug)
                return True
            return False
    
    # Drug Transfer methods
    
    def create_transfer(self, transfer_data: Dict[str, Any], pharmacist_id: uuid.UUID) -> DrugTransfer:
        """
        Create a new drug transfer record.
        CRITICAL: Uses explicit transaction boundary for data integrity.
        """
        with self.db.begin():
            db_transfer = DrugTransfer(
                **transfer_data,
                pharmacist_id=pharmacist_id
            )
            self.db.add(db_transfer)
            self.db.flush()
            self.db.refresh(db_transfer)
            return db_transfer
    
    def list_transfers(self, skip: int = 0, limit: int = 100) -> List[DrugTransfer]:
        """
        Get all drug transfers with pagination.
        
        WARNING: This method uses OFFSET-based pagination which is inefficient for large datasets.
        Use list_transfers_with_cursor() for production workloads with extensive transfer history.
        """
        return self.db.query(DrugTransfer).options(
            # joinedload for many-to-one relationships to prevent N+1 queries
            joinedload(DrugTransfer.drug),
            joinedload(DrugTransfer.pharmacist)
        ).offset(skip).limit(limit).all()
    
    def list_transfers_with_cursor(
        self, 
        cursor: Optional[Union[datetime, uuid.UUID]] = None, 
        limit: int = 100,
        cursor_type: str = "timestamp"
    ) -> Dict[str, Any]:
        """
        Get drug transfers using KEYSET/CURSOR-based pagination for optimal performance.
        
        This method provides efficient pagination through potentially large transfer history
        datasets by using indexed columns to avoid expensive OFFSET operations.
        
        Args:
            cursor: The cursor value from the previous page (timestamp or ID)
            limit: Maximum number of records to return
            cursor_type: Either "timestamp" (transfer_date) or "id" for cursor positioning
            
        Returns:
            Dict containing 'transfers' list and 'next_cursor' for subsequent pagination
        """
        query = self.db.query(DrugTransfer).options(
            # joinedload for many-to-one: prevents N+1 queries with single JOIN
            joinedload(DrugTransfer.drug),
            joinedload(DrugTransfer.pharmacist)
        )
        
        # Apply cursor-based filtering for scalable pagination
        if cursor:
            if cursor_type == "timestamp":
                # Use transfer_date index for chronological pagination
                query = query.filter(DrugTransfer.transfer_date < cursor)
                query = query.order_by(desc(DrugTransfer.transfer_date))
            else:  # cursor_type == "id"
                # Use primary key index for stable pagination
                query = query.filter(DrugTransfer.id < cursor)
                query = query.order_by(desc(DrugTransfer.id))
        else:
            # Default ordering for first page (most recent first)
            if cursor_type == "timestamp":
                query = query.order_by(desc(DrugTransfer.transfer_date))
            else:
                query = query.order_by(desc(DrugTransfer.id))
        
        # Fetch one extra record to determine if there's a next page
        transfers = query.limit(limit + 1).all()
        
        has_next = len(transfers) > limit
        if has_next:
            transfers = transfers[:-1]  # Remove the extra record
        
        # Calculate next cursor
        next_cursor = None
        if has_next and transfers:
            last_transfer = transfers[-1]
            next_cursor = last_transfer.transfer_date if cursor_type == "timestamp" else last_transfer.id
        
        return {
            "transfers": transfers,
            "next_cursor": next_cursor,
            "has_next": has_next,
            "cursor_type": cursor_type
        }
    
    def get_transfer_by_id(self, transfer_id: uuid.UUID) -> Optional[DrugTransfer]:
        """
        Get a single drug transfer by ID.
        """
        return self.db.query(DrugTransfer).filter(DrugTransfer.id == transfer_id).first() 