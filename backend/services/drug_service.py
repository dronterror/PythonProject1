from typing import List, Dict, Any, Optional
import uuid
import logging

from repositories.drug_repository import DrugRepository
from cache import CacheService
from exceptions import (
    DrugNotFoundError, DrugAlreadyExistsError, InsufficientStockError,
    InvalidStockQuantityError, InvalidTransferError
)
from models import Drug, DrugTransfer
from schemas import DrugCreate, DrugUpdate, DrugTransferCreate

logger = logging.getLogger(__name__)


class DrugService:
    """
    Service class for drug and inventory management business logic.
    Handles complex operations, business rules, and cache management.
    """
    
    def __init__(self, drug_repo: DrugRepository):
        self.drug_repo = drug_repo
    
    def create_drug(self, drug_data: DrugCreate) -> Drug:
        """
        Create a new drug with business validation.
        
        Args:
            drug_data: Drug creation data
            
        Returns:
            Created drug
            
        Raises:
            DrugAlreadyExistsError: If drug with same name/form/strength exists
            InvalidStockQuantityError: If stock quantities are invalid
        """
        # Business rule: Validate stock quantities
        if drug_data.current_stock < 0:
            raise InvalidStockQuantityError(drug_data.current_stock)
        
        if drug_data.low_stock_threshold < 0:
            raise InvalidStockQuantityError(drug_data.low_stock_threshold)
        
        # Check for duplicate drug
        existing_drug = self.drug_repo.get_by_name_form_strength(
            drug_data.name, drug_data.form, drug_data.strength
        )
        if existing_drug:
            raise DrugAlreadyExistsError(
                drug_data.name, drug_data.form, drug_data.strength
            )
        
        # Create the drug
        drug_dict = drug_data.dict()
        new_drug = self.drug_repo.create(drug_dict)
        
        # Invalidate drug-related caches
        CacheService.invalidate_drug_caches()
        
        logger.info(f"Created drug: {new_drug.name} ({new_drug.form}, {new_drug.strength})")
        return new_drug
    
    def get_drug_by_id(self, drug_id: uuid.UUID) -> Drug:
        """
        Get a single drug by ID.
        
        Args:
            drug_id: Drug ID
            
        Returns:
            Drug object
            
        Raises:
            DrugNotFoundError: If drug doesn't exist
        """
        drug = self.drug_repo.get_by_id(drug_id)
        if not drug:
            raise DrugNotFoundError(str(drug_id))
        return drug
    
    def update_drug(self, drug_id: uuid.UUID, update_data: DrugUpdate) -> Drug:
        """
        Update a drug with business validation.
        
        Args:
            drug_id: Drug ID
            update_data: Update data
            
        Returns:
            Updated drug
            
        Raises:
            DrugNotFoundError: If drug doesn't exist
            InvalidStockQuantityError: If stock quantities are invalid
        """
        # Validate the drug exists
        existing_drug = self.drug_repo.get_by_id(drug_id)
        if not existing_drug:
            raise DrugNotFoundError(str(drug_id))
        
        # Validate stock quantities if provided
        update_dict = update_data.dict(exclude_unset=True)
        
        if 'current_stock' in update_dict and update_dict['current_stock'] < 0:
            raise InvalidStockQuantityError(update_dict['current_stock'])
        
        if 'low_stock_threshold' in update_dict and update_dict['low_stock_threshold'] < 0:
            raise InvalidStockQuantityError(update_dict['low_stock_threshold'])
        
        # Update the drug
        updated_drug = self.drug_repo.update(drug_id, update_dict)
        
        # Invalidate drug-related caches
        CacheService.invalidate_drug_caches()
        
        logger.info(f"Updated drug {drug_id}")
        return updated_drug
    
    def list_drugs(self, skip: int = 0, limit: int = 100) -> List[Drug]:
        """
        Get all drugs with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of drugs
        """
        return self.drug_repo.list_all(skip, limit)
    
    def get_formulary(self) -> List[Dict[str, Any]]:
        """
        Get the formulary (lightweight drug list for prescribing) with caching.
        
        Returns:
            List of formulary entries
        """
        # Try cache first
        cached_formulary = CacheService.get_formulary()
        if cached_formulary:
            logger.debug("Returning formulary from cache")
            return cached_formulary
        
        # Cache miss - get from database
        formulary_data = self.drug_repo.get_formulary_data()
        
        # Cache the result
        CacheService.set_formulary(formulary_data)
        logger.debug("Cached formulary data")
        
        return formulary_data
    
    def get_inventory_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get real-time inventory status with caching.
        
        Returns:
            Dictionary mapping drug_id to inventory status
        """
        # Try cache first
        cached_inventory = CacheService.get_inventory_status()
        if cached_inventory:
            logger.debug("Returning inventory status from cache")
            return cached_inventory
        
        # Cache miss - get from database
        inventory_data = self.drug_repo.get_inventory_status()
        
        # Cache the result
        CacheService.set_inventory_status(inventory_data)
        logger.debug("Cached inventory status")
        
        return inventory_data
    
    def get_low_stock_drugs(self) -> List[Drug]:
        """
        Get drugs with low stock levels.
        
        Returns:
            List of drugs below their low stock threshold
        """
        return self.drug_repo.list_low_stock()
    
    def update_stock(self, drug_id: uuid.UUID, new_stock: int) -> Drug:
        """
        Update drug stock level with validation.
        
        Args:
            drug_id: Drug ID
            new_stock: New stock level
            
        Returns:
            Updated drug
            
        Raises:
            DrugNotFoundError: If drug doesn't exist
            InvalidStockQuantityError: If stock quantity is invalid
        """
        if new_stock < 0:
            raise InvalidStockQuantityError(new_stock)
        
        drug = self.drug_repo.get_by_id(drug_id)
        if not drug:
            raise DrugNotFoundError(str(drug_id))
        
        updated_drug = self.drug_repo.update_stock(drug_id, new_stock)
        
        # Invalidate drug-related caches
        CacheService.invalidate_drug_caches()
        
        logger.info(f"Updated stock for drug {drug_id}: {drug.current_stock} -> {new_stock}")
        return updated_drug
    
    def transfer_drug_stock(self, transfer_data: DrugTransferCreate, pharmacist_id: uuid.UUID) -> DrugTransfer:
        """
        Transfer drug stock between wards with business validation.
        
        Args:
            transfer_data: Transfer details
            pharmacist_id: ID of the pharmacist performing the transfer
            
        Returns:
            Created transfer record
            
        Raises:
            DrugNotFoundError: If drug doesn't exist
            InvalidTransferError: If transfer is invalid
            InsufficientStockError: If not enough stock for transfer
        """
        # Validate the drug exists
        drug = self.drug_repo.get_by_id(transfer_data.drug_id)
        if not drug:
            raise DrugNotFoundError(str(transfer_data.drug_id))
        
        # Business rules validation
        if transfer_data.quantity <= 0:
            raise InvalidTransferError("Transfer quantity must be positive")
        
        if transfer_data.source_ward == transfer_data.destination_ward:
            raise InvalidTransferError("Source and destination wards cannot be the same")
        
        # Check if there's enough stock for the transfer
        if drug.current_stock < transfer_data.quantity:
            raise InsufficientStockError(
                drug.name,
                transfer_data.quantity,
                drug.current_stock
            )
        
        # Perform the transfer
        try:
            # 1. Decrement stock (simulating transfer from source ward)
            updated_drug = self.drug_repo.decrement_stock(transfer_data.drug_id, transfer_data.quantity)
            if not updated_drug:
                raise InsufficientStockError(
                    drug.name,
                    transfer_data.quantity,
                    drug.current_stock
                )
            
            # 2. Create transfer record
            transfer_dict = transfer_data.dict()
            transfer_record = self.drug_repo.create_transfer(transfer_dict, pharmacist_id)
            
            # 3. Invalidate drug-related caches
            CacheService.invalidate_drug_caches()
            
            logger.info(
                f"Transferred {transfer_data.quantity} units of {drug.name} "
                f"from {transfer_data.source_ward} to {transfer_data.destination_ward}"
            )
            
            return transfer_record
            
        except Exception as e:
            logger.error(f"Failed to transfer drug stock: {e}")
            # In a real implementation, we'd rollback any partial changes
            raise
    
    def get_drug_transfers(self, skip: int = 0, limit: int = 100) -> List[DrugTransfer]:
        """
        Get drug transfer history with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of drug transfers
        """
        return self.drug_repo.list_transfers(skip, limit)
    
    def get_drug_usage_analytics(self, drug_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get analytics for a specific drug (placeholder for complex analytics).
        
        Args:
            drug_id: Drug ID
            
        Returns:
            Dictionary with drug usage analytics
            
        Raises:
            DrugNotFoundError: If drug doesn't exist
        """
        drug = self.drug_repo.get_by_id(drug_id)
        if not drug:
            raise DrugNotFoundError(str(drug_id))
        
        # This would typically involve complex queries and calculations
        # For now, return basic information
        
        is_low_stock = drug.current_stock <= drug.low_stock_threshold
        
        return {
            "drug_id": str(drug_id),
            "drug_name": drug.name,
            "current_stock": drug.current_stock,
            "low_stock_threshold": drug.low_stock_threshold,
            "is_low_stock": is_low_stock,
            "stock_status": "critical" if drug.current_stock == 0 else "low" if is_low_stock else "adequate",
            "stock_percentage": (drug.current_stock / max(drug.low_stock_threshold * 2, 1)) * 100
        }
    
    def delete_drug(self, drug_id: uuid.UUID) -> bool:
        """
        Delete a drug (soft delete in most cases).
        
        Args:
            drug_id: Drug ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            DrugNotFoundError: If drug doesn't exist
        """
        drug = self.drug_repo.get_by_id(drug_id)
        if not drug:
            raise DrugNotFoundError(str(drug_id))
        
        # Business rule: Should check if drug is referenced in active orders
        # For now, just proceed with deletion
        
        success = self.drug_repo.delete(drug_id)
        
        if success:
            # Invalidate drug-related caches
            CacheService.invalidate_drug_caches()
            logger.info(f"Deleted drug {drug_id}")
        
        return success 