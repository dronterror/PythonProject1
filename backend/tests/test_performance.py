import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session
from models import User, UserRole, Drug, MedicationOrder, OrderStatus, MedicationAdministration
import time
import uuid

class TestNPlusOneQueryFix:
    """Test that N+1 query issues have been resolved with eager loading."""
    
    def test_get_multi_by_doctor_uses_eager_loading(self, db_session, sample_doctor, sample_drug):
        """
        Test that get_multi_by_doctor uses eager loading to prevent N+1 queries.
        This test verifies that all administrations are loaded in a single query.
        """
        # Track database queries
        query_count = 0
        
        def count_queries(name, *args, **kwargs):
            nonlocal query_count
            query_count += 1
        
        # Listen for database queries
        event.listen(db_session.bind, 'after_cursor_execute', count_queries)
        
        try:
            # Create multiple orders with administrations
            orders = []
            for i in range(3):
                order = MedicationOrder(
                    patient_name=f"Patient {i}",
                    drug_id=sample_drug.id,
                    dosage=2,
                    schedule="Every 8 hours",
                    status=OrderStatus.active,
                    doctor_id=sample_doctor.id
                )
                db_session.add(order)
                db_session.flush()  # Get the order ID
                
                # Add administrations for each order
                for j in range(2):
                    admin = MedicationAdministration(
                        order_id=order.id,
                        nurse_id=sample_doctor.id  # Using doctor as nurse for test
                    )
                    db_session.add(admin)
                
                orders.append(order)
            
            db_session.commit()
            
            # Reset query counter
            query_count = 0
            
            # Import and call the function
            from crud import get_multi_by_doctor
            result = get_multi_by_doctor(db_session, sample_doctor.id if isinstance(sample_doctor.id, uuid.UUID) else uuid.UUID(str(sample_doctor.id)))
            
            # Verify results
            assert len(result) == 3
            for order in result:
                assert len(order.administrations) == 2
            
            # Verify that administrations are loaded (not lazy-loaded)
            # If lazy loading was used, accessing administrations would trigger additional queries
            # With eager loading, they should already be loaded
            for order in result:
                # This should not trigger additional queries if eager loading is working
                admin_count = len(order.administrations)
                assert admin_count == 2
            
            # The query count should be minimal (1 for orders + 1 for administrations)
            # If N+1 was happening, we'd see 1 + N queries where N = number of orders
            assert query_count <= 3, f"Expected <= 3 queries, got {query_count} (N+1 query detected)"
            
        finally:
            # Remove the event listener
            event.remove(db_session.bind, 'after_cursor_execute', count_queries)
    
    def test_get_multi_active_uses_eager_loading(self, db_session, sample_doctor, sample_drug):
        """
        Test that get_multi_active uses eager loading to prevent N+1 queries.
        """
        # Track database queries
        query_count = 0
        
        def count_queries(name, *args, **kwargs):
            nonlocal query_count
            query_count += 1
        
        # Listen for database queries
        event.listen(db_session.bind, 'after_cursor_execute', count_queries)
        
        try:
            # Create multiple active orders with administrations
            orders = []
            for i in range(3):
                order = MedicationOrder(
                    patient_name=f"Patient {i}",
                    drug_id=sample_drug.id,
                    dosage=2,
                    schedule="Every 8 hours",
                    status=OrderStatus.active,
                    doctor_id=sample_doctor.id
                )
                db_session.add(order)
                db_session.flush()
                
                # Add administrations for each order
                for j in range(2):
                    admin = MedicationAdministration(
                        order_id=order.id,
                        nurse_id=sample_doctor.id
                    )
                    db_session.add(admin)
                
                orders.append(order)
            
            db_session.commit()
            
            # Reset query counter
            query_count = 0
            
            # Import and call the function
            from crud import get_multi_active
            result = get_multi_active(db_session)
            
            # Verify results
            assert len(result) == 3
            for order in result:
                assert len(order.administrations) == 2
            
            # Verify that administrations are loaded
            for order in result:
                admin_count = len(order.administrations)
                assert admin_count == 2
            
            # The query count should be minimal
            assert query_count <= 3, f"Expected <= 3 queries, got {query_count} (N+1 query detected)"
            
        finally:
            # Remove the event listener
            event.remove(db_session.bind, 'after_cursor_execute', count_queries)
    
    def test_get_medication_orders_uses_eager_loading(self, db_session, sample_doctor, sample_drug):
        """
        Test that get_medication_orders uses eager loading to prevent N+1 queries.
        """
        # Track database queries
        query_count = 0
        
        def count_queries(name, *args, **kwargs):
            nonlocal query_count
            query_count += 1
        
        # Listen for database queries
        event.listen(db_session.bind, 'after_cursor_execute', count_queries)
        
        try:
            # Create multiple orders with administrations
            orders = []
            for i in range(3):
                order = MedicationOrder(
                    patient_name=f"Patient {i}",
                    drug_id=sample_drug.id,
                    dosage=2,
                    schedule="Every 8 hours",
                    status=OrderStatus.active,
                    doctor_id=sample_doctor.id
                )
                db_session.add(order)
                db_session.flush()
                
                # Add administrations for each order
                for j in range(2):
                    admin = MedicationAdministration(
                        order_id=order.id,
                        nurse_id=sample_doctor.id
                    )
                    db_session.add(admin)
                
                orders.append(order)
            
            db_session.commit()
            
            # Reset query counter
            query_count = 0
            
            # Import and call the function
            from crud import get_medication_orders
            result = get_medication_orders(db_session, skip=0, limit=10)
            
            # Verify results
            assert len(result) >= 3
            for order in result:
                assert len(order.administrations) == 2
            
            # Verify that administrations are loaded
            for order in result:
                admin_count = len(order.administrations)
                assert admin_count == 2
            
            # The query count should be minimal
            assert query_count <= 3, f"Expected <= 3 queries, got {query_count} (N+1 query detected)"
            
        finally:
            # Remove the event listener
            event.remove(db_session.bind, 'after_cursor_execute', count_queries)
    
    def test_get_medication_order_uses_eager_loading(self, db_session, sample_doctor, sample_drug):
        """
        Test that get_medication_order uses eager loading for single order retrieval.
        """
        # Track database queries
        query_count = 0
        
        def count_queries(name, *args, **kwargs):
            nonlocal query_count
            query_count += 1
        
        # Listen for database queries
        event.listen(db_session.bind, 'after_cursor_execute', count_queries)
        
        try:
            # Create an order with administrations
            order = MedicationOrder(
                patient_name="Test Patient",
                drug_id=sample_drug.id,
                dosage=2,
                schedule="Every 8 hours",
                status=OrderStatus.active,
                doctor_id=sample_doctor.id
            )
            db_session.add(order)
            db_session.flush()
            
            # Add administrations
            for j in range(3):
                admin = MedicationAdministration(
                    order_id=order.id,
                    nurse_id=sample_doctor.id
                )
                db_session.add(admin)
            
            db_session.commit()
            
            # Reset query counter
            query_count = 0
            
            # Import and call the function
            from crud import get_medication_order
            result = get_medication_order(db_session, order.id)
            
            # Verify results
            assert result is not None
            assert len(result.administrations) == 3
            
            # Verify that administrations are loaded
            admin_count = len(result.administrations)
            assert admin_count == 3
            
            # The query count should be minimal (1 for order + 1 for administrations)
            assert query_count <= 3, f"Expected <= 3 queries, got {query_count} (N+1 query detected)"
            
        finally:
            # Remove the event listener
            event.remove(db_session.bind, 'after_cursor_execute', count_queries) 