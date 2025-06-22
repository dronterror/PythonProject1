import pytest
from fastapi import status
from models import User, UserRole, Drug, MedicationOrder, OrderStatus, MedicationAdministration

class TestAdministrationsEndpoints:
    """Test cases for the administrations router endpoints."""
    
    def test_administer_drug_with_insufficient_stock(self, client, db_session, sample_nurse, sample_doctor):
        """
        Test that attempting to administer a drug with insufficient stock returns 400 Bad Request.
        Arrange: Create a drug with current_stock = 0. Create an order for that drug.
        Act: Attempt to call POST /administrations/ as a nurse to administer that order.
        Assert: Verify that the response status code is exactly 400 Bad Request and that the error detail message indicates insufficient stock.
        """
        # Override the database dependency to use our test session
        from dependencies import get_db
        from main import app
        app.dependency_overrides[get_db] = lambda: db_session
        
        # Arrange: Create a drug with zero stock
        drug_with_no_stock = Drug(
            name="Test Drug",
            form="Tablet",
            strength="100mg",
            current_stock=0,  # Zero stock
            low_stock_threshold=10
        )
        db_session.add(drug_with_no_stock)
        db_session.commit()
        db_session.refresh(drug_with_no_stock)
        
        # Create an order for the drug with no stock
        order = MedicationOrder(
            patient_name="Test Patient",
            drug_id=drug_with_no_stock.id,
            dosage=1,
            schedule="Every 8 hours",
            status=OrderStatus.active,
            doctor_id=sample_doctor.id
        )
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        
        # Act: Attempt to administer the drug with insufficient stock
        response = client.post(
            "/api/administrations/",
            headers={"X-API-Key": sample_nurse.api_key},
            json={"order_id": str(order.id)}
        )
        
        # Assert: Verify 400 Bad Request with insufficient stock message
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Insufficient stock" in response.json()["detail"]
        
        # Verify that no administration was created
        administrations = db_session.query(MedicationAdministration).filter(
            MedicationAdministration.order_id == order.id
        ).all()
        assert len(administrations) == 0
        
        # Verify that drug stock remains unchanged
        db_session.refresh(drug_with_no_stock)
        assert drug_with_no_stock.current_stock == 0
        
        # Clean up override
        app.dependency_overrides.clear()
    
    def test_nurse_cannot_access_without_api_key(self, client):
        """
        Test that administrations endpoint requires API key authentication.
        Arrange: No API key provided.
        Act: Attempt to call POST /administrations/ without API key.
        Assert: Verify status code is 401 Unauthorized.
        """
        # Act: Attempt to access administrations endpoint without API key
        response = client.post(
            "/api/administrations/",
            json={"order_id": "00000000-0000-0000-0000-000000000001"}
        )
        
        # Assert: Verify 401 Unauthorized response
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Missing API Key" in response.json()["detail"]
    
    def test_doctor_cannot_administer_medication(self, client, sample_doctor, db_session, sample_drug):
        """
        Test that a doctor cannot access the nurse-only administrations endpoint.
        Arrange: Create a doctor user and an active order.
        Act: Attempt to call POST /administrations/ with doctor's API key.
        Assert: Verify status code is 403 Forbidden.
        """
        # Override the database dependency to use our test session
        from dependencies import get_db
        from main import app
        app.dependency_overrides[get_db] = lambda: db_session
        
        # Arrange: Create an active order
        order = MedicationOrder(
            patient_name="Test Patient",
            drug_id=sample_drug.id,
            dosage=1,
            schedule="Every 8 hours",
            status=OrderStatus.active,
            doctor_id=sample_doctor.id
        )
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        
        # Act: Attempt to access nurse-only endpoint with doctor API key
        response = client.post(
            "/api/administrations/",
            headers={"X-API-Key": sample_doctor.api_key},
            json={"order_id": str(order.id)}
        )
        
        # Assert: Verify 403 Forbidden response
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]
        
        # Clean up override
        app.dependency_overrides.clear()
    
    def test_pharmacist_cannot_administer_medication(self, client, sample_pharmacist, db_session, sample_drug, sample_doctor):
        """
        Test that a pharmacist cannot access the nurse-only administrations endpoint.
        Arrange: Create a pharmacist user and an active order.
        Act: Attempt to call POST /administrations/ with pharmacist's API key.
        Assert: Verify status code is 403 Forbidden.
        """
        # Override the database dependency to use our test session
        from dependencies import get_db
        from main import app
        app.dependency_overrides[get_db] = lambda: db_session
        
        # Arrange: Create an active order
        order = MedicationOrder(
            patient_name="Test Patient",
            drug_id=sample_drug.id,
            dosage=1,
            schedule="Every 8 hours",
            status=OrderStatus.active,
            doctor_id=sample_doctor.id
        )
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        
        # Act: Attempt to access nurse-only endpoint with pharmacist API key
        response = client.post(
            "/api/administrations/",
            headers={"X-API-Key": sample_pharmacist.api_key},
            json={"order_id": str(order.id)}
        )
        
        # Assert: Verify 403 Forbidden response
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]
        
        # Clean up override
        app.dependency_overrides.clear()
    
    def test_administer_nonexistent_order(self, client, sample_nurse):
        """
        Test that attempting to administer a nonexistent order returns 404 Not Found.
        Arrange: Create a nurse user.
        Act: Attempt to call POST /administrations/ with a nonexistent order_id.
        Assert: Verify that the response status code is exactly 404 Not Found.
        """
        # Act: Attempt to administer a nonexistent order
        response = client.post(
            "/api/administrations/",
            headers={"X-API-Key": sample_nurse.api_key},
            json={"order_id": "00000000-0000-0000-0000-000000999999"}  # Nonexistent order ID
        )
        
        # Assert: Verify 404 Not Found response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Order not found" in response.json()["detail"]
    
    def test_administer_inactive_order(self, client, sample_nurse, db_session, sample_drug, sample_doctor):
        """
        Test that attempting to administer an inactive order returns 400 Bad Request.
        Arrange: Create a completed order.
        Act: Attempt to call POST /administrations/ for the completed order.
        Assert: Verify that the response status code is exactly 400 Bad Request.
        """
        # Override the database dependency to use our test session
        from dependencies import get_db
        from main import app
        app.dependency_overrides[get_db] = lambda: db_session
        
        # Arrange: Create a completed order
        order = MedicationOrder(
            patient_name="Test Patient",
            drug_id=sample_drug.id,
            dosage=1,
            schedule="Every 8 hours",
            status=OrderStatus.completed,  # Inactive order
            doctor_id=sample_doctor.id
        )
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        
        # Act: Attempt to administer the inactive order
        response = client.post(
            "/api/administrations/",
            headers={"X-API-Key": sample_nurse.api_key},
            json={"order_id": str(order.id)}
        )
        
        # Assert: Verify 400 Bad Request response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Order is not active" in response.json()["detail"]
        
        # Clean up override
        app.dependency_overrides.clear() 