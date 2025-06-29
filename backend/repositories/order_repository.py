from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import and_, func
from typing import List, Optional, Dict, Any
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
            joinedload(MedicationOrder.drug),
            joinedload(MedicationOrder.doctor),
            selectinload(MedicationOrder.administrations).joinedload(MedicationAdministration.nurse)
        ).filter(MedicationOrder.id == order_id).first()
    
    def create(self, order_data: Dict[str, Any], doctor_id: uuid.UUID) -> MedicationOrder:
        """
        Create a new medication order.
        """
        db_order = MedicationOrder(
            **order_data,
            doctor_id=doctor_id,
            status=OrderStatus.active
        )
        self.db.add(db_order)
        self.db.commit()
        self.db.refresh(db_order)
        
        # Return with relationships loaded
        return self.get_by_id(db_order.id)
    
    def list_active(self, skip: int = 0, limit: int = 100) -> List[MedicationOrder]:
        """
        Get all active orders with optimized eager loading.
        Uses selectinload for one-to-many relationships to prevent N+1 queries.
        """
        return self.db.query(MedicationOrder).options(
            # Use joinedload for many-to-one relationships (more efficient)
            joinedload(MedicationOrder.drug),
            joinedload(MedicationOrder.doctor),
            # Use selectinload for one-to-many relationships to avoid cartesian products
            selectinload(MedicationOrder.administrations).joinedload(MedicationAdministration.nurse)
        ).filter(
            MedicationOrder.status == OrderStatus.active
        ).offset(skip).limit(limit).all()
    
    def list_by_doctor(self, doctor_id: uuid.UUID) -> List[MedicationOrder]:
        """
        Get all orders created by a specific doctor with optimized loading.
        """
        return self.db.query(MedicationOrder).options(
            joinedload(MedicationOrder.drug),
            selectinload(MedicationOrder.administrations).joinedload(MedicationAdministration.nurse)
        ).filter(MedicationOrder.doctor_id == doctor_id).all()
    
    def list_active_for_mar(self) -> List[MedicationOrder]:
        """
        Get active orders for Medication Administration Record (MAR).
        Optimized for nurse/pharmacist dashboard.
        """
        return self.db.query(MedicationOrder).options(
            joinedload(MedicationOrder.drug),
            joinedload(MedicationOrder.doctor),
            selectinload(MedicationOrder.administrations).joinedload(MedicationAdministration.nurse)
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
            # selectinload is used for one-to-many to avoid cartesian products
            # while still loading all administrations in a separate optimized query
            selectinload(MedicationOrder.administrations).joinedload(MedicationAdministration.nurse)
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
        """
        order = self.db.query(MedicationOrder).filter(MedicationOrder.id == order_id).first()
        if order:
            order.status = status
            self.db.commit()
            self.db.refresh(order)
            return self.get_by_id(order_id)  # Return with relationships loaded
        return None
    
    def delete(self, order_id: uuid.UUID) -> bool:
        """
        Delete an order (soft delete by setting status to discontinued).
        """
        order = self.db.query(MedicationOrder).filter(MedicationOrder.id == order_id).first()
        if order:
            order.status = OrderStatus.discontinued
            self.db.commit()
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