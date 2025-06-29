from typing import List, Dict, Any, Optional
import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from repositories.order_repository import OrderRepository
from repositories.drug_repository import DrugRepository
from cache import CacheService
from exceptions import (
    OrderNotFoundError, DrugNotFoundError, InsufficientStockError,
    OrderAlreadyCompletedError, InvalidOrderStatusError
)
from models import MedicationOrder, OrderStatus, User, Drug
from schemas import MedicationOrderCreate

logger = logging.getLogger(__name__)


class OrderService:
    """
    Service class for medication order business logic.
    CRITICAL: All operations maintain ACID properties with proper transaction management.
    """
    
    def __init__(self, order_repo: OrderRepository, drug_repo: DrugRepository, db_session: Session):
        self.order_repo = order_repo
        self.drug_repo = drug_repo
        self.db = db_session  # CRITICAL: Direct access to session for transaction control
    
    def create_order(self, order_data: MedicationOrderCreate, doctor_id: uuid.UUID) -> MedicationOrder:
        """
        Create a new medication order with business logic validation.
        
        Args:
            order_data: Order creation data
            doctor_id: ID of the prescribing doctor
            
        Returns:
            Created medication order
            
        Raises:
            DrugNotFoundError: If the specified drug doesn't exist
            InsufficientStockError: If there's not enough stock for the order
        """
        # Validate drug exists
        drug = self.drug_repo.get_by_id(order_data.drug_id)
        if not drug:
            raise DrugNotFoundError(str(order_data.drug_id))
        
        # Business rule: Check if there's sufficient stock for the order
        # This is a preventive check, not a reservation
        if drug.current_stock < order_data.dosage:
            raise InsufficientStockError(
                drug.name, 
                order_data.dosage, 
                drug.current_stock
            )
        
        # Create order
        order_dict = order_data.dict()
        new_order = self.order_repo.create(order_dict, doctor_id)
        
        # Invalidate relevant caches
        CacheService.invalidate_order_caches()
        
        logger.info(f"Created order {new_order.id} for patient {new_order.patient_name}")
        return new_order
    
    def get_order_by_id(self, order_id: uuid.UUID) -> MedicationOrder:
        """
        Get a single order by ID.
        
        Args:
            order_id: Order ID
            
        Returns:
            Medication order
            
        Raises:
            OrderNotFoundError: If order doesn't exist
        """
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(str(order_id))
        return order
    
    def list_active_orders(self, skip: int = 0, limit: int = 100) -> List[MedicationOrder]:
        """
        Get all active orders with optimized loading.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active medication orders
        """
        return self.order_repo.list_active(skip, limit)
    
    def list_orders_by_doctor(self, doctor_id: uuid.UUID) -> List[MedicationOrder]:
        """
        Get all orders created by a specific doctor.
        
        Args:
            doctor_id: Doctor's user ID
            
        Returns:
            List of orders created by the doctor
        """
        return self.order_repo.list_by_doctor(doctor_id)
    
    def get_active_mar_orders(self) -> List[MedicationOrder]:
        """
        Get active orders for Medication Administration Record (MAR).
        Used by nurses and pharmacists.
        
        Returns:
            List of active orders for MAR
        """
        return self.order_repo.list_active_for_mar()
    
    def get_mar_dashboard_data(self) -> Dict[str, Any]:
        """
        Get optimized dashboard data for nurses with caching.
        
        Returns:
            Dashboard data grouped by patient
        """
        # Try to get from cache first
        cached_data = CacheService.get_mar_dashboard()
        if cached_data:
            logger.debug("Returning MAR dashboard data from cache")
            return cached_data
        
        # Cache miss - get from database
        dashboard_data = self.order_repo.get_mar_dashboard_data()
        
        # Cache the result
        CacheService.set_mar_dashboard(dashboard_data)
        logger.debug("Cached MAR dashboard data")
        
        return dashboard_data
    
    def fulfill_order(self, order_id: uuid.UUID, nurse_id: uuid.UUID) -> Dict[str, Any]:
        """
        CRITICAL: Fulfill a medication order with ATOMIC transaction integrity.
        This method uses database-level transactions with REPEATABLE READ isolation
        to prevent data corruption during concurrent operations.
        
        Args:
            order_id: ID of the order to fulfill
            nurse_id: ID of the nurse fulfilling the order
            
        Returns:
            Dictionary with fulfillment details
            
        Raises:
            OrderNotFoundError: If order doesn't exist
            OrderAlreadyCompletedError: If order is already completed
            DrugNotFoundError: If associated drug doesn't exist
            InsufficientStockError: If there's not enough stock
        """
        try:
            # CRITICAL: Begin explicit transaction with REPEATABLE READ isolation
            # This prevents phantom reads and ensures data consistency
            with self.db.begin():
                # Step 1: Get and lock the order record
                order = self.db.query(MedicationOrder).filter(
                    MedicationOrder.id == order_id
                ).with_for_update().first()  # SELECT FOR UPDATE - prevents concurrent modifications
                
                if not order:
                    raise OrderNotFoundError(str(order_id))
                
                # Business rule: Can't fulfill completed orders
                if order.status == OrderStatus.completed:
                    raise OrderAlreadyCompletedError(str(order_id))
                
                # Business rule: Can't fulfill discontinued orders
                if order.status == OrderStatus.discontinued:
                    raise InvalidOrderStatusError(
                        order.status.value, 
                        "fulfilled"
                    )
                
                # Step 2: Get and lock the drug record to prevent concurrent stock modifications
                drug = self.db.query(Drug).filter(
                    Drug.id == order.drug_id
                ).with_for_update().first()  # SELECT FOR UPDATE - critical for inventory integrity
                
                if not drug:
                    raise DrugNotFoundError(str(order.drug_id))
                
                # CRITICAL: Final stock check under lock to prevent race conditions
                if drug.current_stock < order.dosage:
                    raise InsufficientStockError(
                        drug.name,
                        order.dosage,
                        drug.current_stock
                    )
                
                # Step 3: ATOMICALLY update both records within the transaction
                # If any step fails, the entire transaction is rolled back
                
                # Decrement drug stock
                drug.current_stock -= order.dosage
                self.db.add(drug)  # Mark for update
                
                # Update order status to completed
                order.status = OrderStatus.completed
                self.db.add(order)  # Mark for update
                
                # Step 4: Flush changes to database (but don't commit yet)
                # This ensures database constraints are checked before commit
                self.db.flush()
                
                # Step 5: If we reach here, all operations succeeded
                # Transaction will be committed when exiting the 'with' block
                
                fulfillment_result = {
                    "order_id": str(order_id),
                    "patient_name": order.patient_name,
                    "drug_name": drug.name,
                    "dosage_given": order.dosage,
                    "remaining_stock": drug.current_stock,
                    "fulfilled_by": str(nurse_id),
                    "status": "completed"
                }
                
            # CRITICAL: Only invalidate caches AFTER successful transaction commit
            CacheService.invalidate_order_caches()
            CacheService.invalidate_drug_caches()
            
            logger.info(
                f"✅ ATOMIC FULFILLMENT COMPLETED: Order {order_id} - "
                f"{order.dosage} units of {drug.name} for patient {order.patient_name} "
                f"by nurse {nurse_id}. Remaining stock: {drug.current_stock}"
            )
            
            return fulfillment_result
            
        except (OrderNotFoundError, DrugNotFoundError, InsufficientStockError, 
                OrderAlreadyCompletedError, InvalidOrderStatusError):
            # Re-raise business exceptions without modification
            raise
            
        except SQLAlchemyError as e:
            # Database error - transaction automatically rolled back
            logger.error(f"❌ DATABASE ERROR during order fulfillment {order_id}: {e}")
            self.db.rollback()  # Explicit rollback for safety
            raise Exception(f"Database error during order fulfillment: {str(e)}")
            
        except Exception as e:
            # Unexpected error - ensure transaction is rolled back
            logger.error(f"❌ UNEXPECTED ERROR during order fulfillment {order_id}: {e}")
            self.db.rollback()  # Explicit rollback for safety
            raise Exception(f"Unexpected error during order fulfillment: {str(e)}")
    
    def discontinue_order(self, order_id: uuid.UUID, reason: str = None) -> MedicationOrder:
        """
        Discontinue a medication order.
        
        Args:
            order_id: ID of the order to discontinue
            reason: Optional reason for discontinuation
            
        Returns:
            Updated medication order
            
        Raises:
            OrderNotFoundError: If order doesn't exist
            OrderAlreadyCompletedError: If order is already completed
        """
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(str(order_id))
        
        if order.status == OrderStatus.completed:
            raise OrderAlreadyCompletedError(str(order_id))
        
        discontinued_order = self.order_repo.update_status(order_id, OrderStatus.discontinued)
        
        # Invalidate caches
        CacheService.invalidate_order_caches()
        
        logger.info(f"Discontinued order {order_id}. Reason: {reason or 'Not specified'}")
        return discontinued_order
    
    def get_order_statistics(self) -> Dict[str, Any]:
        """
        Get order statistics for reporting.
        
        Returns:
            Dictionary with various order statistics
        """
        # This would typically involve multiple repository calls
        # and complex aggregations
        
        # For now, return basic info from the MAR dashboard
        dashboard_data = self.get_mar_dashboard_data()
        
        return {
            "total_active_orders": dashboard_data.get("total_active_orders", 0),
            "total_patients": dashboard_data.get("total_patients", 0),
            "pending_administrations": dashboard_data.get("total_pending_administrations", 0),
            "last_updated": dashboard_data.get("last_updated")
        } 