import pytest
from fastapi import status
from models import User, UserRole, Drug, MedicationOrder, OrderStatus

class TestOrdersEndpoints:
    """Test cases for the orders router endpoints."""
    
    def test_doctor_can_see_only_their_own_orders(self, client, db_session, sample_doctor, sample_drug):
        """
        Test that a doctor can only see orders they created.
        Arrange: Create two different doctors and an order for each.
        Act: Make an API call to GET /orders/my-orders/ with the first doctor's API key.
        Assert: Verify status code is 200, response contains exactly one order, and that order belongs to the correct doctor.
        """
        # Override the database dependency to use our test session
        from dependencies import get_db
        from main import app
        app.dependency_overrides[get_db] = lambda: db_session

        # Arrange: Create a second doctor
        second_doctor = User(
            email="doctor2@test.com",
            hashed_password="hashed_password",
            api_key="doctor2_api_key_456",
            role=UserRole.doctor
        )
        db_session.add(second_doctor)
        db_session.commit()
        db_session.refresh(second_doctor)
        
        # Create an order for the first doctor
        order1 = MedicationOrder(
            patient_name="Patient 1",
            drug_id=sample_drug.id,
            dosage=2,
            schedule="Every 8 hours",
            status=OrderStatus.active,
            doctor_id=sample_doctor.id
        )
        db_session.add(order1)
        
        # Create an order for the second doctor
        order2 = MedicationOrder(
            patient_name="Patient 2",
            drug_id=sample_drug.id,
            dosage=1,
            schedule="Every 12 hours",
            status=OrderStatus.active,
            doctor_id=second_doctor.id
        )
        db_session.add(order2)
        db_session.commit()
        
        # Act: Make API call with first doctor's API key
        response = client.get(
            "/api/orders/my-orders/",
            headers={"X-API-Key": sample_doctor.api_key}
        )
        
        # Assert: Verify response
        assert response.status_code == status.HTTP_200_OK
        orders = response.json()
        # Count only orders created by sample_doctor in this test (check by patient name)
        doctor_orders = [order for order in orders if order["patient_name"] == "Patient 1"]
        assert len(doctor_orders) == 1
        assert doctor_orders[0]["patient_name"] == "Patient 1"
        assert doctor_orders[0]["doctor_id"] == sample_doctor.id
        
        # Clean up override
        app.dependency_overrides.clear()
    
    def test_nurse_cannot_access_doctor_orders_endpoint(self, client, sample_nurse):
        """
        Test that a nurse cannot access the doctor-only orders endpoint.
        Arrange: Create a nurse user.
        Act: Attempt to call GET /orders/my-orders/ with the nurse's API key.
        Assert: Verify status code is exactly 403 Forbidden.
        """
        # Act: Attempt to access doctor-only endpoint with nurse API key
        response = client.get(
            "/api/orders/my-orders/",
            headers={"X-API-Key": sample_nurse.api_key}
        )
        
        # Assert: Verify 403 Forbidden response
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]
    
    def test_nurse_can_access_active_mar(self, client, db_session, sample_nurse, sample_doctor, sample_drug):
        """
        Test that a nurse can access the active MAR endpoint.
        Arrange: Create a nurse user and an active order.
        Act: Make API call to GET /orders/active-mar/ with nurse's API key.
        Assert: Verify status code is 200.
        """
        # Arrange: Create an active order
        order = MedicationOrder(
            patient_name="Test Patient",
            drug_id=sample_drug.id,
            dosage=2,
            schedule="Every 8 hours",
            status=OrderStatus.active,
            doctor_id=sample_doctor.id
        )
        db_session.add(order)
        db_session.commit()
        
        # Act: Make API call with nurse's API key
        response = client.get(
            "/api/orders/active-mar/",
            headers={"X-API-Key": sample_nurse.api_key}
        )
        
        # Assert: Verify 200 OK response
        assert response.status_code == status.HTTP_200_OK
    
    def test_pharmacist_can_access_active_mar(self, client, db_session, sample_pharmacist, sample_doctor, sample_drug):
        """
        Test that a pharmacist can access the active MAR endpoint.
        Arrange: Create a pharmacist user and an active order.
        Act: Make API call to GET /orders/active-mar/ with pharmacist's API key.
        Assert: Verify status code is 200.
        """
        # Arrange: Create an active order
        order = MedicationOrder(
            patient_name="Test Patient",
            drug_id=sample_drug.id,
            dosage=2,
            schedule="Every 8 hours",
            status=OrderStatus.active,
            doctor_id=sample_doctor.id
        )
        db_session.add(order)
        db_session.commit()
        
        # Act: Make API call with pharmacist's API key
        response = client.get(
            "/api/orders/active-mar/",
            headers={"X-API-Key": sample_pharmacist.api_key}
        )
        
        # Assert: Verify 200 OK response
        assert response.status_code == status.HTTP_200_OK
    
    def test_doctor_cannot_access_active_mar(self, client, sample_doctor):
        """
        Test that a doctor cannot access the active MAR endpoint (nurse/pharmacist only).
        Arrange: Create a doctor user.
        Act: Attempt to call GET /orders/active-mar/ with doctor's API key.
        Assert: Verify status code is 403 Forbidden.
        """
        # Act: Attempt to access nurse/pharmacist-only endpoint with doctor API key
        response = client.get(
            "/api/orders/active-mar/",
            headers={"X-API-Key": sample_doctor.api_key}
        )
        
        # Assert: Verify 403 Forbidden response
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied" in response.json()["detail"]
    
    def test_unauthorized_access_without_api_key(self, client):
        """
        Test that endpoints require API key authentication.
        Arrange: No API key provided.
        Act: Make API calls without API key.
        Assert: Verify status code is 401 Unauthorized.
        """
        # Test doctor endpoint without API key
        response = client.get("/api/orders/my-orders/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Missing API Key" in response.json()["detail"]
        
        # Test MAR endpoint without API key
        response = client.get("/api/orders/active-mar/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Missing API Key" in response.json()["detail"]
    
    def test_invalid_api_key_returns_401(self, client):
        """
        Test that invalid API keys return 401 Unauthorized.
        Arrange: Use an invalid API key.
        Act: Make API calls with invalid API key.
        Assert: Verify status code is 401 Unauthorized.
        """
        # Test with invalid API key
        response = client.get(
            "/api/orders/my-orders/",
            headers={"X-API-Key": "invalid_api_key"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid API Key" in response.json()["detail"]
        
        response = client.get(
            "/api/orders/active-mar/",
            headers={"X-API-Key": "invalid_api_key"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid API Key" in response.json()["detail"] 