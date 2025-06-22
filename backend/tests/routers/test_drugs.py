import pytest
from fastapi import status
from models import User, UserRole, Drug

class TestDrugsEndpoints:
    """Test cases for the drugs router endpoints."""
    
    def test_doctor_cannot_create_drug(self, client, sample_doctor):
        """
        Test that a doctor cannot create drugs (pharmacist-only endpoint).
        Arrange: Create a 'doctor' user.
        Act: Attempt to call POST /drugs/ with the doctor's API key.
        Assert: Verify that the response status code is exactly 403 Forbidden.
        """
        # Act: Attempt to create a drug with doctor's API key
        drug_data = {
            "name": "Test Drug",
            "form": "Tablet",
            "strength": "100mg",
            "current_stock": 50,
            "low_stock_threshold": 10
        }
        
        response = client.post(
            "/api/drugs/",
            headers={"X-API-Key": sample_doctor.api_key},
            json=drug_data
        )
        
        # Assert: Verify 403 Forbidden response
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]
    
    def test_nurse_cannot_create_drug(self, client, sample_nurse):
        """
        Test that a nurse cannot create drugs (pharmacist-only endpoint).
        Arrange: Create a 'nurse' user.
        Act: Attempt to call POST /drugs/ with the nurse's API key.
        Assert: Verify that the response status code is exactly 403 Forbidden.
        """
        # Act: Attempt to create a drug with nurse's API key
        drug_data = {
            "name": "Test Drug",
            "form": "Tablet",
            "strength": "100mg",
            "current_stock": 50,
            "low_stock_threshold": 10
        }
        
        response = client.post(
            "/api/drugs/",
            headers={"X-API-Key": sample_nurse.api_key},
            json=drug_data
        )
        
        # Assert: Verify 403 Forbidden response
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]
    
    def test_doctor_cannot_update_drug(self, client, sample_doctor, db_session, sample_drug):
        """
        Test that a doctor cannot update drugs (pharmacist-only endpoint).
        Arrange: Create a doctor user and an existing drug.
        Act: Attempt to call PUT /drugs/{drug_id} with the doctor's API key.
        Assert: Verify that the response status code is exactly 403 Forbidden.
        """
        # Override the database dependency to use our test session
        from dependencies import get_db
        from main import app
        app.dependency_overrides[get_db] = lambda: db_session
        
        # Act: Attempt to update a drug with doctor's API key
        update_data = {
            "current_stock": 100
        }
        
        response = client.put(
            f"/api/drugs/{sample_drug.id}",
            headers={"X-API-Key": sample_doctor.api_key},
            json=update_data
        )
        
        # Assert: Verify 403 Forbidden response
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]
        
        # Clean up override
        app.dependency_overrides.clear()
    
    def test_doctor_cannot_access_low_stock_endpoint(self, client, sample_doctor):
        """
        Test that a doctor cannot access the low stock endpoint (pharmacist-only).
        Arrange: Create a doctor user.
        Act: Attempt to call GET /drugs/low-stock with the doctor's API key.
        Assert: Verify that the response status code is exactly 403 Forbidden.
        """
        # Act: Attempt to access low stock endpoint with doctor's API key
        response = client.get(
            "/api/drugs/low-stock",
            headers={"X-API-Key": sample_doctor.api_key}
        )
        
        # Assert: Verify 403 Forbidden response
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]
    
    def test_nurse_cannot_access_low_stock_endpoint(self, client, sample_nurse):
        """
        Test that a nurse cannot access the low stock endpoint (pharmacist-only).
        Arrange: Create a nurse user.
        Act: Attempt to call GET /drugs/low-stock with the nurse's API key.
        Assert: Verify that the response status code is exactly 403 Forbidden.
        """
        # Act: Attempt to access low stock endpoint with nurse's API key
        response = client.get(
            "/api/drugs/low-stock",
            headers={"X-API-Key": sample_nurse.api_key}
        )
        
        # Assert: Verify 403 Forbidden response
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in response.json()["detail"]
    
    def test_create_drug_with_negative_stock_validation(self, client, sample_pharmacist):
        """
        Test that creating a drug with negative stock values is rejected by validation.
        Arrange: Create a pharmacist user.
        Act: Attempt to call POST /drugs/ with negative stock values.
        Assert: Verify that the response status code is exactly 422 Unprocessable Entity.
        """
        # Act: Attempt to create a drug with negative stock
        drug_data = {
            "name": "Test Drug",
            "form": "Tablet",
            "strength": "100mg",
            "current_stock": -10,  # Negative stock
            "low_stock_threshold": 5
        }
        
        response = client.post(
            "/api/drugs/",
            headers={"X-API-Key": sample_pharmacist.api_key},
            json=drug_data
        )
        
        # Assert: Verify 422 Unprocessable Entity response (validation error)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_drug_with_negative_threshold_validation(self, client, sample_pharmacist):
        """
        Test that creating a drug with negative low stock threshold is rejected by validation.
        Arrange: Create a pharmacist user.
        Act: Attempt to call POST /drugs/ with negative low stock threshold.
        Assert: Verify that the response status code is exactly 422 Unprocessable Entity.
        """
        # Act: Attempt to create a drug with negative threshold
        drug_data = {
            "name": "Test Drug",
            "form": "Tablet",
            "strength": "100mg",
            "current_stock": 50,
            "low_stock_threshold": -5  # Negative threshold
        }
        
        response = client.post(
            "/api/drugs/",
            headers={"X-API-Key": sample_pharmacist.api_key},
            json=drug_data
        )
        
        # Assert: Verify 422 Unprocessable Entity response (validation error)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_drug_with_negative_stock_validation(self, client, sample_pharmacist, db_session, sample_drug):
        """
        Test that updating a drug with negative stock values is rejected by validation.
        Arrange: Create a pharmacist user and an existing drug.
        Act: Attempt to call PUT /drugs/{drug_id} with negative stock values.
        Assert: Verify that the response status code is exactly 422 Unprocessable Entity.
        """
        # Override the database dependency to use our test session
        from dependencies import get_db
        from main import app
        app.dependency_overrides[get_db] = lambda: db_session
        
        # Act: Attempt to update a drug with negative stock
        update_data = {
            "current_stock": -5  # Negative stock
        }
        
        response = client.put(
            f"/api/drugs/{sample_drug.id}",
            headers={"X-API-Key": sample_pharmacist.api_key},
            json=update_data
        )
        
        # Assert: Verify 422 Unprocessable Entity response (validation error)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Clean up override
        app.dependency_overrides.clear()
    
    def test_unauthorized_access_without_api_key(self, client):
        """
        Test that drugs endpoints require API key authentication.
        Arrange: No API key provided.
        Act: Make API calls without API key.
        Assert: Verify status code is 401 Unauthorized.
        """
        # Test create drug endpoint without API key
        drug_data = {
            "name": "Test Drug",
            "form": "Tablet",
            "strength": "100mg",
            "current_stock": 50,
            "low_stock_threshold": 10
        }
        
        response = client.post("/api/drugs/", json=drug_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Missing API Key" in response.json()["detail"]
        
        # Test get drugs endpoint without API key
        response = client.get("/api/drugs/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Missing API Key" in response.json()["detail"]
        
        # Test low stock endpoint without API key
        response = client.get("/api/drugs/low-stock")
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
        drug_data = {
            "name": "Test Drug",
            "form": "Tablet",
            "strength": "100mg",
            "current_stock": 50,
            "low_stock_threshold": 10
        }
        
        response = client.post(
            "/api/drugs/",
            headers={"X-API-Key": "invalid_api_key"},
            json=drug_data
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid API Key" in response.json()["detail"]
        
        response = client.get(
            "/api/drugs/",
            headers={"X-API-Key": "invalid_api_key"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid API Key" in response.json()["detail"] 