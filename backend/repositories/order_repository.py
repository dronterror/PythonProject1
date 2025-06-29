from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import and_, func, desc
from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime

from models import MedicationOrder, OrderStatus, Drug, User, MedicationAdministration


class OrderRepository:
    """
    Repository for medication order data access.
    Handles all database operations related to orders with optimized queries.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, order_id: uuid.UUID) -> Optional[MedicationOrder]:
        """
        Get a single order by ID with eager loading to prevent N+1 queries.
        """
        return self.db.query(MedicationOrder).options(
            # joinedload for many-to-one: efficient single query with JOIN
            joinedload(MedicationOrder.drug),
            joinedload(MedicationOrder.doctor),
            # selectinload for one-to-many: avoids cartesian products by using 
            # a separate SELECT with WHERE...IN clause, preventing data duplication
            # over the wire and maintaining query performance
            selectinload(MedicationOrder.administrations),
            # Load the nurse relationship for each administration using a nested selectinload
            # This creates a third optimized query: SELECT users WHERE id IN (admin_user_ids)
            selectinload(MedicationOrder.administrations).selectinload(MedicationAdministration.nurse)
        ).filter(MedicationOrder.id == order_id).first()
    
    def create(self, order_data: Dict[str, Any], doctor_id: uuid.UUID) -> MedicationOrder:
        """
        Create a new medication order.
        CRITICAL: Uses explicit transaction boundary for data integrity.
        """
        with self.db.begin():
            db_order = MedicationOrder(
                **order_data,
                doctor_id=doctor_id,
                status=OrderStatus.active
            )
            self.db.add(db_order)
            self.db.flush()
            self.db.refresh(db_order)
            
            # Load relationships within transaction context to prevent race conditions
            db_order_with_relations = self.db.query(MedicationOrder).options(
                joinedload(MedicationOrder.drug),
                joinedload(MedicationOrder.doctor),
                selectinload(MedicationOrder.administrations),
                selectinload(MedicationOrder.administrations).selectinload(MedicationAdministration.nurse)
            ).filter(MedicationOrder.id == db_order.id).first()
            
            return db_order_with_relations
    
    def list_active(self, skip: int = 0, limit: int = 100) -> List[MedicationOrder]:
        """
        Get all active orders with optimized eager loading.
        
        CRITICAL: selectinload is used for one-to-many relationships to prevent the N+1 problem
        while avoiding cartesian products that joinedload would create. selectinload executes
        a separate WHERE...IN query which is much more efficient than duplicating order data
        for each administration record across the network.
        """
        return self.db.query(MedicationOrder).options(
            # joinedload for many-to-one relationships: single query with JOIN
            joinedload(MedicationOrder.drug),
            joinedload(MedicationOrder.doctor),
            # selectinload for one-to-many: prevents data duplication and cartesian products
            # This will execute: SELECT * FROM medication_administrations WHERE order_id IN (...)
            selectinload(MedicationOrder.administrations),
            # Nested selectinload to load nurses for administrations efficiently
            selectinload(MedicationOrder.administrations).selectinload(MedicationAdministration.nurse)
        ).filter(
            MedicationOrder.status == OrderStatus.active
        ).offset(skip).limit(limit).all()
    
    def list_by_doctor(self, doctor_id: uuid.UUID) -> List[MedicationOrder]:
        """
        Get all orders created by a specific doctor with optimized loading.
        """
        return self.db.query(MedicationOrder).options(
            joinedload(MedicationOrder.drug),
            # selectinload prevents N+1 while avoiding cartesian product data explosion
            selectinload(MedicationOrder.administrations),
            selectinload(MedicationOrder.administrations).selectinload(MedicationAdministration.nurse)
        ).filter(MedicationOrder.doctor_id == doctor_id).all()
    
    def list_active_for_mar(self) -> List[MedicationOrder]:
        """
        Get active orders for Medication Administration Record (MAR).
        Optimized for nurse/pharmacist dashboard.
        """
        return self.db.query(MedicationOrder).options(
            joinedload(MedicationOrder.drug),
            joinedload(MedicationOrder.doctor),
            # selectinload is MANDATORY for one-to-many to avoid network bandwidth waste
            # and database performance degradation from cartesian product generation
            selectinload(MedicationOrder.administrations),
            selectinload(MedicationOrder.administrations).selectinload(MedicationAdministration.nurse)
        ).filter(MedicationOrder.status == OrderStatus.active).all()
    
    def get_mar_dashboard_data(self) -> Dict[str, Any]:
        """
        Get optimized dashboard data for nurses, grouped by patient.
        This function is optimized to prevent N+1 queries using a single complex query.
        """
        # Use a single query with all necessary joins and loading strategies
        active_orders = self.db.query(MedicationOrder).options(
            # joinedload is used for many-to-one relationships to minimize queries
            joinedload(MedicationOrder.drug),
            joinedload(MedicationOrder.doctor),
            # selectinload is CRITICAL here: it avoids cartesian products by using
            # separate WHERE...IN queries instead of duplicating order data for each
            # administration record, drastically reducing network traffic
            selectinload(MedicationOrder.administrations),
            selectinload(MedicationOrder.administrations).selectinload(MedicationAdministration.nurse)
        ).filter(MedicationOrder.status == OrderStatus.active).all()
        
        # Group by patient in Python (more efficient than complex SQL grouping)
        patients_data = {}
        total_pending_administrations = 0
        
        for order in active_orders:
            patient_name = order.patient_name
            
            if patient_name not in patients_data:
                patients_data[patient_name] = {
                    "name": patient_name,
                    "bed_number": f"Bed-{hash(patient_name) % 100:02d}",  # Mock bed assignment
                    "active_orders": []
                }
            
            # Count pending administrations (orders without administrations)
            if not order.administrations:
                total_pending_administrations += 1
            
            patients_data[patient_name]["active_orders"].append(order)
        
        return {
            "patients": list(patients_data.values()),
            "total_patients": len(patients_data),
            "total_active_orders": len(active_orders),
            "total_pending_administrations": total_pending_administrations,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def update_status(self, order_id: uuid.UUID, status: OrderStatus) -> Optional[MedicationOrder]:
        """
        Update the status of an order.
        CRITICAL: Uses explicit transaction boundary for data integrity.
        """
        with self.db.begin():
            order = self.db.query(MedicationOrder).filter(MedicationOrder.id == order_id).first()
            if order:
                order.status = status
                self.db.flush()
                self.db.refresh(order)
                
                # Load relationships within transaction context to prevent race conditions
                order_with_relations = self.db.query(MedicationOrder).options(
                    joinedload(MedicationOrder.drug),
                    joinedload(MedicationOrder.doctor),
                    selectinload(MedicationOrder.administrations),
                    selectinload(MedicationOrder.administrations).selectinload(MedicationAdministration.nurse)
                ).filter(MedicationOrder.id == order_id).first()
                
                return order_with_relations
            return None
    
    def delete(self, order_id: uuid.UUID) -> bool:
        """
        Delete an order (soft delete by setting status to discontinued).
        CRITICAL: Uses explicit transaction boundary for data integrity.
        """
        with self.db.begin():
            order = self.db.query(MedicationOrder).filter(MedicationOrder.id == order_id).first()
            if order:
                order.status = OrderStatus.discontinued
                return True
            return False
    
    def count_active_by_drug(self, drug_id: uuid.UUID) -> int:
        """
        Count active orders for a specific drug.
        """
        return self.db.query(MedicationOrder).filter(
            and_(
                MedicationOrder.drug_id == drug_id,
                MedicationOrder.status == OrderStatus.active
            )
        ).count()
    
    def list_active_with_cursor(
        self, 
        cursor: Optional[Union[datetime, uuid.UUID]] = None, 
        limit: int = 100,
        cursor_type: str = "timestamp"
    ) -> Dict[str, Any]:
        """
        Get active orders using KEYSET/CURSOR-based pagination instead of OFFSET.
        
        OFFSET-based pagination becomes inefficient with large datasets because the database
        must count and skip all preceding rows. Cursor-based pagination uses indexed columns
        to create a WHERE clause that directly positions the query, maintaining O(log n) performance
        regardless of page depth.
        
        Args:
            cursor: The cursor value from the previous page (timestamp or ID)
            limit: Maximum number of records to return
            cursor_type: Either "timestamp" (created_at) or "id" for cursor positioning
            
        Returns:
            Dict containing 'orders' list and 'next_cursor' for subsequent pagination
        """
        query = self.db.query(MedicationOrder).options(
            joinedload(MedicationOrder.drug),
            joinedload(MedicationOrder.doctor),
            # selectinload prevents data duplication across network for one-to-many relationships
            selectinload(MedicationOrder.administrations),
            selectinload(MedicationOrder.administrations).selectinload(MedicationAdministration.nurse)
        ).filter(MedicationOrder.status == OrderStatus.active)
        
        # Apply cursor-based filtering for scalable pagination
        if cursor:
            if cursor_type == "timestamp":
                # Use created_at index for chronological pagination
                query = query.filter(MedicationOrder.created_at < cursor)
                query = query.order_by(desc(MedicationOrder.created_at))
            else:  # cursor_type == "id"
                # Use primary key index for stable pagination
                query = query.filter(MedicationOrder.id < cursor)
                query = query.order_by(desc(MedicationOrder.id))
        else:
            # Default ordering for first page
            if cursor_type == "timestamp":
                query = query.order_by(desc(MedicationOrder.created_at))
            else:
                query = query.order_by(desc(MedicationOrder.id))
        
        # Fetch one extra record to determine if there's a next page
        orders = query.limit(limit + 1).all()
        
        has_next = len(orders) > limit
        if has_next:
            orders = orders[:-1]  # Remove the extra record
        
        # Calculate next cursor
        next_cursor = None
        if has_next and orders:
            last_order = orders[-1]
            next_cursor = last_order.created_at if cursor_type == "timestamp" else last_order.id
        
        return {
            "orders": orders,
            "next_cursor": next_cursor,
            "has_next": has_next,
            "cursor_type": cursor_type
        } 